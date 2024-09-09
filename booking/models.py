from django.db import models
from django.utils import timezone

from management.models import Item, BillBook

# Create your models here.


class DateTimeBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(DateTimeBaseModel):
    bill_number = models.IntegerField(unique=True, db_index=True)
    book = models.ForeignKey(
        BillBook, on_delete=models.CASCADE, related_name="orders", db_index=True
    )
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    comment = models.TextField(null=True, blank=True)
    total_order_price = models.FloatField(default=0.0)
    received_amount = models.FloatField(default=0.0)
    is_special_price = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bill_number} {self.customer_name}"

    class Meta:
        ordering = ["bill_number"]


class OrderItem(DateTimeBaseModel):
    booking = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", db_index=True
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="order_items")
    order_quantity = models.IntegerField(default=0)
    delivered_quantity = models.IntegerField(default=0)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.booking.bill_number} - {self.item.base_item.name}"
