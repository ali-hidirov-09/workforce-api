from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Worker

@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'work_type', 'is_active']
    list_filter = ['role', 'work_type', 'is_active']
    search_fields = ['username', 'first_name', 'last_name']
    ordering = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('first_name', 'last_name', 'number', 'living_address')}),
        ('Ish ma\'lumotlari', {'fields': ('role', 'work_type', 'percentage_work', 'work_day', 'rest_day')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
