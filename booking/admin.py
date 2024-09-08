from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Order, OrderItem


# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("item", "item__base_item", "booking")
    
@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ["bill_number"]
    
