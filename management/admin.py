from django.contrib import admin

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
    ]
    search_fields = ["name"]


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
class BillBookAdmin(admin.ModelAdmin):
    inlines = [OrderInlineAdmin]
    list_display = [
        "book_number",
        "user",
    ]
    search_fields = ["book_number"]
