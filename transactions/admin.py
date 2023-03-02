from django.contrib import admin
from .models import Coupon

# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active']