from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from management.models import UserDeposits

# Register your models here.


class UserDepositsInline(admin.TabularInline):
    model = UserDeposits
    extra = 0


@admin.register(User)
class UserModelAdmin(UserAdmin):
    inlines = [
        UserDepositsInline,
    ]
