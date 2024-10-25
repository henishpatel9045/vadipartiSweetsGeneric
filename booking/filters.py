from django.contrib import admin
from datetime import datetime
from django.contrib.auth import get_user_model

from booking.models import OrderItem

User = get_user_model()


class OrderCommentFilter(admin.SimpleListFilter):
    title = "Has Comment"
    parameter_name = "has_comment"

    def lookups(self, request, model_admin):
        return (
            ("1", "Yes"),
            ("0", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.exclude(comment="")
        if self.value() == "0":
            return queryset.filter(comment="")
        return queryset
    

class InputFilter(admin.SimpleListFilter):
    template = "admin/input_filter.html"

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice["query_parts"] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class OrderDealerFilter(InputFilter):
    title = "Dealer"
    parameter_name = "dealer"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(book__user__username=self.value())
        return queryset

class OrderBillBookFilter(InputFilter):
    title = "Bill Book"
    parameter_name = "bill_book"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(book__book_number=int(self.value()))
        return queryset

class OrderIsFullyDispatchedListFilter(admin.SimpleListFilter):
    title = "Is Fully Dispatched"
    parameter_name = "is_fully_dispatched"

    def lookups(self, request, model_admin):
        return (
            ("True", "Yes"),
            ("False", "No"),
        )

    def queryset(self, request, queryset):
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
        # get all the key of above res where order_quantity == delivered_quantity
        fully_dispatched = [
            key
            for key in res
            if res[key]["order_quantity"] == res[key]["delivered_quantity"]
        ]
        if self.value() == "True":
            return queryset.filter(bill_number__in=fully_dispatched)
        if self.value() == "False":
            return queryset.exclude(bill_number__in=fully_dispatched)
        return queryset
        

class OrderIsPartialDispatchedListFilter(admin.SimpleListFilter):
    title = "Is Partial Dispatched"
    parameter_name = "is_partial_dispatched"

    def lookups(self, request, model_admin):
        return (
            ("True", "Yes"),
            ("False", "No"),
        )

    def queryset(self, request, queryset):
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
        partial_dispatched = [
            key
            for key in res
            if res[key]["delivered_quantity"] > 0 and res[key]["order_quantity"] != res[key]["delivered_quantity"]
        ]
        if self.value() == "True":
            return queryset.filter(bill_number__in=partial_dispatched)
        if self.value() == "False":
            return queryset.exclude(bill_number__in=partial_dispatched)
        return queryset