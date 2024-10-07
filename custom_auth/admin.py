from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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
