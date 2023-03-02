from django.db import models
from django.conf import settings
# Create your models here.

class PaymentMethod(models.Model):
    CARD = 'CARD'
    ACCOUNT = 'ACCOUNT'
    PAYMENT_METHOD_TYPES = [
        (CARD, '카드'),
        (ACCOUNT, '계좌'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_METHOD_TYPES)

class Card(models.Model):
    payment_method = models.OneToOneField(PaymentMethod, on_delete=models.CASCADE, null=True)
    card_company = models.CharField(max_length=50)
    card_number = models.CharField(max_length=16)
    expiry_month = models.PositiveIntegerField()
    expiry_year = models.PositiveIntegerField()
    cvc = models.PositiveIntegerField()


class Account(models.Model):
    payment_method = models.OneToOneField(PaymentMethod, on_delete=models.CASCADE, null=True)
    bank_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=20)

class Coupon(models.Model):
    DISCOUNT_TYPE_PERCENTAGE = 'PERCENTAGE'
    DISCOUNT_TYPE_FIXED_AMOUNT = 'FIXED_AMOUNT'
    DISCOUNT_TYPES = [
        (DISCOUNT_TYPE_PERCENTAGE, 'Percentage'),
        (DISCOUNT_TYPE_FIXED_AMOUNT, 'Fixed Amount'),
    ]
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

class UserCoupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    used_date = models.DateTimeField(null=True, blank=True)

class Transaction(models.Model):
    TRANSACTION_TYPE_CHARGE = 'CHARGE'
    TRANSACTION_TYPE_PAYMENT = 'PAYMENT'
    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPE_CHARGE, 'Charge'),
        (TRANSACTION_TYPE_PAYMENT, 'Payment'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    used_balance = models.IntegerField(default=0, blank=True)
    actual_amount = models.IntegerField(default=0, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)

    class Meta:
        ordering = ['-date']