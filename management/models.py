from django.db import models
from django.utils import timezone

from vadipartiSweets.constants import BILL_BOOK_SIZE, PAYMENT_OPTIONS


# Create your models here.
class ItemBase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="items", null=True, blank=True)
    stop_taking_order = models.BooleanField(default=False)
    order_index = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["order_index"]


class Item(models.Model):
    base_item = models.ForeignKey(
        ItemBase, on_delete=models.CASCADE, related_name="variants"
    )
    box_size = models.CharField(
        max_length=20,
        help_text="Box size in grams i.e. for 500gms, enter 500, for 1kg, enter 1000.",
    )
    price = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.base_item} {self.box_size}"


class BillBook(models.Model):
    user = models.ForeignKey(
        "custom_auth.User", on_delete=models.CASCADE, db_index=True
    )
    book_number = models.IntegerField(db_index=True, unique=True)
    total_bills = models.IntegerField(default=BILL_BOOK_SIZE)

    def __str__(self):
        return f"{self.book_number}"

    class Meta:
        ordering = ["book_number"]


class UserDeposits(models.Model):
    DEPOSIT_TYPES = [
        ("For Order", "For Order"),
        ("Dealer", "Dealer"),
    ]

    user = models.ForeignKey(
        "custom_auth.User", on_delete=models.CASCADE, db_index=True
    )
    is_deposited_by_dealer = models.BooleanField(default=True)
    order = models.ForeignKey(
        "booking.Order", on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    payment_option = models.CharField(
        choices=PAYMENT_OPTIONS, default="Cash", max_length=20
    )
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(default=timezone.now)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.amount}"

    class Meta:
        ordering = ["-date"]


class DailyReadyItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="ready_items")
    quantity = models.IntegerField(default=0)
    comment = models.TextField(default="", blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.item} - {self.quantity}"

    class Meta:
        ordering = ["-date"]
