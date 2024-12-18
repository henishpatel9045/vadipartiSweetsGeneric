from typing import Any
from django.contrib import admin
from django.db import transaction, models
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django_object_actions import DjangoObjectActions
from django.utils.html import format_html

from booking.utils import update_price_of_booking
from .models import Order, OrderItem
from .filters import OrderDealerFilter, OrderBillBookFilter, OrderCommentFilter, OrderIsPartialDispatchedListFilter, OrderIsFullyDispatchedListFilter

# Register your models here.

admin.site.site_header = "Vadiparti Sweets 2024"
admin.site.site_title = "Vadiparti Sweets 2024"
admin.site.index_title = "Vadiparti Sweets 2024"
admin.site.site_url = "/home"


@admin.register(OrderItem)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = [
        "booking",
        "item",
        "order_quantity",
        "delivered_quantity",
        "created_at",
        "updated_at",
    ]
    list_filter = ["item__base_item", "booking__book__user"]
    search_fields = [
        "booking__bill_number",
    ]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("item", "item__base_item", "booking")
        )


@admin.register(Order)
class OrderModelAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = [
        "bill_number",
        "customer_name",
        "total_order_price",
        # "received_amount",
        "is_fully_dispatched",
        "is_partial_dispatched",
        "is_special_price",
        "payment_deposited_by_customer",
        "has_comment",
        "comment",
        "created_at",
        "updated_at",
    ]
    list_filter = (
        OrderDealerFilter,
        OrderBillBookFilter,
        OrderCommentFilter,
        OrderIsFullyDispatchedListFilter,
        OrderIsPartialDispatchedListFilter,
        "is_special_price",
        "payment_deposited_by_customer",
    )
    change_actions = [
        "full_dispatch",
        "update_order_total_price",
    ]
    actions = ["full_dispatch_changelist", "update_order_total_price_changelist"]
    search_fields = ["bill_number", "customer_name", "customer_phone"]

    def has_comment(self, obj: Order) -> bool:
        if bool(obj.comment):
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')

    def full_dispatch(self, request: HttpRequest, obj: Order) -> None:
        try:
            with transaction.atomic():
                order_items: list[OrderItem] = obj.items.all()
                order_items.update(delivered_quantity=models.F("order_quantity"))
                self.message_user(request, "Order dispatched successfully")
        except Exception as e:
            self.message_user(request, f"Error: {e}", level="ERROR")

    full_dispatch.label = "Full Dispatch"

    def update_order_total_price(self, request: HttpRequest, obj: Order) -> None:
        try:
            if not obj.is_special_price:
                update_price_of_booking(obj)
                self.message_user(request, "Order total price updated successfully")
        except Exception as e:
            self.message_user(request, f"Error: {e}", level="ERROR")

    def full_dispatch_changelist(
        self, request: HttpRequest, queryset: QuerySet[Order]
    ) -> None:
        try:
            with transaction.atomic():
                order_items = OrderItem.objects.filter(booking__in=queryset)
                order_items.update(delivered_quantity=models.F("order_quantity"))
                self.message_user(request, "Orders dispatched successfully")
        except Exception as e:
            self.message_user(request, f"Error: {e}", level="ERROR")

    def update_order_total_price_changelist(
        self, request: HttpRequest, queryset: QuerySet[Order]
    ) -> None:
        try:
            with transaction.atomic():
                for order in queryset:
                    if not order.is_special_price:
                        update_price_of_booking(order)
                self.message_user(request, "Order total price updated successfully")
        except Exception as e:
            self.message_user(request, f"Error: {e}", level="ERROR")

    def changelist_view(self, request):
        changelist_order_items = OrderItem.objects.prefetch_related(
            "booking", "item"
        ).all()
        res = {}
        for item in changelist_order_items:
            id = str(item.booking.bill_number)
            if id not in res:
                res[id] = {
                    "order_quantity": 0,
                    "delivered_quantity": 0,
                }
            res[id]["order_quantity"] += item.order_quantity
            res[id]["delivered_quantity"] += item.delivered_quantity
        self.changelist_order_items = res
        return super().changelist_view(request)

    def is_fully_dispatched(self, obj: Order) -> bool:
        if (
            self.changelist_order_items[str(obj.bill_number)]["order_quantity"]
            == self.changelist_order_items[str(obj.bill_number)]["delivered_quantity"]
        ):
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        else:
            return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
        

    def is_partial_dispatched(self, obj: Order) -> bool:
        if (
            self.changelist_order_items[str(obj.bill_number)]["delivered_quantity"] > 0 and self.changelist_order_items[str(obj.bill_number)]["delivered_quantity"] != self.changelist_order_items[str(obj.bill_number)]["order_quantity"]
        ):
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        else:
            return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
