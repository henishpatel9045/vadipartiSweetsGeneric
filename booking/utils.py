import math
from datetime import datetime
from django.conf import settings

from booking.models import Order, OrderItem
from management.models import BillBook, Item
from vadipartiSweets.constants import BILL_BOOK_SIZE


def create_booking(
    bill_number: int,
    customer_name: str,
    items: list[dict[str, Item | str | int]],
    received_amount: float,
    comment: str = "",
    is_special_price: bool = False,
    special_price: float = 0.0,
    user=None,
    order_date: str | None = None,
    phone: str | None = None,
) -> Order:
    """Create a order with items.

    Args:
        bill_number (int): Bill number.
        customer_name (str): Customer name.
        items (list[dict[str, Item | str | int]]): List of items with quantity.
            ```python
            {
                "item": Item,
                "quantity": int,
            }
            ```
        received_amount (float): Received amount.
        comment (str, optional): Comment. Defaults to "".
        is_special_price (bool, optional): Is special price. Defaults to False.
        special_price (float, optional): Special price. Defaults to 0.0.
        order_date (str, optional): Order date. Defaults to None.
        phone (str, optional): Phone number. Defaults to None.
    """
    ALLOW_NEW_ORDER = settings.ALLOW_NEW_ORDER
    if not ALLOW_NEW_ORDER:
        raise Exception("New orders are not allowed. Please contact the admin.")

    try:
        bill_book = BillBook.objects.prefetch_related("user").get(
            book_number=math.ceil(bill_number / BILL_BOOK_SIZE)
        )
    except BillBook.DoesNotExist:
        raise Exception(
            f"Bill book {math.ceil(bill_number / BILL_BOOK_SIZE)} not found."
        )
    if bill_book.user.pk != user.pk:
        raise Exception(f"Bill book {bill_book.book_number} is not assigned to you.")
    booking = Order()
    booking.bill_number = bill_number
    booking.book = bill_book
    booking.customer_name = customer_name
    booking.comment = comment
    booking.received_amount = received_amount
    booking.customer_phone = phone
    if order_date:
        booking.date = datetime.strptime(order_date, "%Y-%m-%d")
    booking.save()
    total_order_amount = 0
    order_items = []
    for item in items:
        booking_item = OrderItem()
        booking_item.booking = booking
        booking_item.item = item["item"]
        booking_item.order_quantity = item["quantity"]
        total_order_amount += item["quantity"] * item["item"].price
        order_items.append(booking_item)
        booking_item.save()

    if is_special_price:
        booking.total_order_price = special_price
    else:
        booking.total_order_price = total_order_amount

    # OrderItem.objects.bulk_create(order_items)
    booking.save()

    return booking


def update_price_of_booking(order: Order) -> Order:
    """Update the price of the order.

    Args:
        order (Order): Booking object.
    """
    total_order_amount = 0
    order_items = OrderItem.objects.prefetch_related("item").filter(booking=order)
    for item in order_items:
        total_order_amount += item.order_quantity * item.item.price

    order.total_order_price = total_order_amount
    order.save()

    return order


def update_booking(
    pk: int | str,
    bill_number: int,
    customer_name: str,
    items: list[dict[str, Item | str | int]],
    received_amount: float,
    comment: str = "",
    is_special_price: bool = False,
    special_price: float = 0.0,
    order_date: str | None = None,
    phone: str | None = None,
) -> Order:
    """Create a order with items.

    Args:
        pk (int): Order id.
        bill_number (int): Bill number.
        customer_name (str): Customer name.
        items (list[dict[str, Item | str | int]]): List of items with quantity.
            ```python
            {
                "item": Item,
                "quantity": int,
            }
            ```
        received_amount (float): Received amount.
        comment (str, optional): Comment. Defaults to "".
        is_special_price (bool, optional): Is special price. Defaults to False.
        special_price (float, optional): Special price. Defaults to 0.0.
        order_date (str, optional): Order date. Defaults to None.
        phone (str, optional): Phone number. Defaults to None.
    """
    ALLOW_UPDATE_ORDER = settings.ALLOW_EDIT_ORDER

    booking = Order.objects.get(pk=pk)
    if booking.is_special_price:
        raise Exception(
            "Special price orders cannot be updated directly. Please contact the admin to update this order."
        )
    booking.customer_name = customer_name
    booking.comment = comment
    booking.received_amount = received_amount
    booking.bill_number = bill_number
    if order_date:
        booking.date = datetime.strptime(order_date, "%Y-%m-%d")
    booking.customer_phone = phone

    if ALLOW_UPDATE_ORDER:
        total_order_amount = 0
        order_items = []
        for item in items:
            if item["order_item"]:
                order_item: OrderItem = item["order_item"]
                order_item.order_quantity = item["quantity"]
                order_item.save()
                total_order_amount += item["quantity"] * item["item"].price
            else:
                booking_item = OrderItem()
                booking_item.booking = booking
                booking_item.item = item["item"]
                booking_item.order_quantity = item["quantity"]
                total_order_amount += item["quantity"] * item["item"].price
                order_items.append(booking_item)

        if is_special_price:
            booking.total_order_price = special_price
        else:
            booking.total_order_price = total_order_amount

    booking.save()

    if ALLOW_UPDATE_ORDER:
        OrderItem.objects.bulk_create(order_items)

    return booking


def delete_order(pk: str | int, user: any):
    """Delete the order.

    Args:
        pk (str|int): Order id.
    """
    ALLOW_DELETE_ORDER = settings.ALLOW_DELETE_ORDER
    if not ALLOW_DELETE_ORDER:
        raise Exception("Deleting orders are not allowed. Please contact the admin.")
    order = Order.objects.prefetch_related("book", "book__user").get(pk=pk)
    if not user.is_superuser:
        if order.book.user.pk != user.pk:
            raise Exception("You are not allowed to delete this order.")
    order.delete()
    return True
