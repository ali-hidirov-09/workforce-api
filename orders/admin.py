from django.contrib import admin
from .models import Order, OrderType

@admin.register(OrderType)
class OrderTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number', 'type', 'status', 'price', 'date', 'worker']
    list_filter = ['status', 'type']
    search_fields = ['name', 'number', 'address']
