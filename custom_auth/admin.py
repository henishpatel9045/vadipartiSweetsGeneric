from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry

from .models import User
from management.models import UserDeposits, BillBook
from .forms import CustomUserCreationForm

# Register your models here.


class UserDepositsInline(admin.TabularInline):
    model = UserDeposits
    extra = 0


class BillBookInline(admin.TabularInline):
    model = BillBook
    extra = 0


@admin.register(User)
class UserModelAdmin(UserAdmin):
    inlines = [
        UserDepositsInline,
        BillBookInline,
    ]
    add_form = CustomUserCreationForm


@admin.register(LogEntry)
class LogEntryModelAdmin(admin.ModelAdmin):
    list_display = (
        "content_type",
        "user",
        "object_repr",
        "action_flag",
        "change_message",
        "action_time",
    )
