from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
        'is_staff',
        'is_active',
        'is_superuser',
        'last_login',
        'date_joined',
    )
    list_editable = (
        'role',
        'is_staff',
        'is_active',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'role'
    )
    