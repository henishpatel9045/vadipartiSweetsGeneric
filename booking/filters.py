from django.contrib import admin
from datetime import datetime
from django.contrib.auth import get_user_model

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
