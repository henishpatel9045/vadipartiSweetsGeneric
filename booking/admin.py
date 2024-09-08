from typing import Any
from django.contrib import admin
from django.db import transaction
from django.db.models.query import QuerySet
from django.db import models
from django.http import HttpRequest
from django_object_actions import DjangoObjectActions

from .models import Order, OrderItem
from .filters import OrderDealerFilter, OrderBillBookFilter

# Register your models here.


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
    list_display = ["bill_number"]
    list_filter = (OrderDealerFilter, OrderBillBookFilter,)
    change_actions = ["full_dispatch"]
    actions = ["full_dispatch_changelist"]
    search_fields = ["bill_number", "customer_name", "customer_phone"]

    def full_dispatch(self, request: HttpRequest, obj: Order) -> None:
        try:
            with transaction.atomic():
                order_items: list[OrderItem] = obj.items.all()
                order_items.update(delivered_quantity=models.F("order_quantity"))
                self.message_user(request, "Order dispatched successfully")
        except Exception as e:
            self.message_user(request, f"Error: {e}", level="ERROR")

    full_dispatch.label = "Full Dispatch"

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
