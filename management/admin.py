from django.contrib import admin
from django.shortcuts import redirect
from django_object_actions import DjangoObjectActions

from booking.models import Order
from .models import ItemBase, Item, BillBook, DailyReadyItem

# Register your models here.


class ReadyItemInlineAdmin(admin.TabularInline):
    model = DailyReadyItem
    extra = 0


@admin.register(Item)
class ItemBaseAdmin(admin.ModelAdmin):
    inlines = [ReadyItemInlineAdmin]
    list_display = [
        "base_item",
        "box_size",
    ]


class ItemInlineAdmin(admin.TabularInline):
    model = Item
    extra = 0


@admin.register(ItemBase)
class ItemBaseAdmin(admin.ModelAdmin):
    inlines = [ItemInlineAdmin]
    list_display = [
        "name",
        "stop_taking_order",
    ]
    search_fields = ["name"]
    list_editable = ["stop_taking_order"]


class OrderInlineAdmin(admin.TabularInline):
    model = Order
    extra = 0
    fields = [
        "bill_number",
        "customer_name",
        "total_order_price",
        "received_amount",
    ]
    show_change_link = True


@admin.register(BillBook)
class BillBookAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [OrderInlineAdmin]
    list_display = [
        "book_number",
        "user",
    ]
    search_fields = [
        "book_number",
        "user__username",
    ]
    change_actions = [
        "print",
    ]
    autocomplete_fields = ["user"]

    def print(self, request, obj: BillBook):
        return redirect(f"/bookings/print?type=book&pk={obj.book_number}")
