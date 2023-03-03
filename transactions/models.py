from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.

class PaymentMethod(models.Model): # 결제 관리
    CARD = 'CARD'
    ACCOUNT = 'ACCOUNT'
    PAYMENT_METHOD_TYPES = [
        (CARD, '카드'),
        (ACCOUNT, '계좌'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_METHOD_TYPES)

class Card(models.Model): # 카드
    payment_method = models.OneToOneField(PaymentMethod, on_delete=models.CASCADE, null=True)
    card_company = models.CharField(max_length=50)
    card_number = models.CharField(max_length=16)
    expiry_month = models.PositiveIntegerField()
    expiry_year = models.PositiveIntegerField()
    cvc = models.PositiveIntegerField()


class Account(models.Model): # 계좌
    payment_method = models.OneToOneField(PaymentMethod, on_delete=models.CASCADE, null=True)
    bank_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=20)

class Coupon(models.Model): # 쿠폰 (admin만 등록 수정 삭제 가능)
    DISCOUNT_TYPE_PERCENTAGE = 'PERCENTAGE'
    DISCOUNT_TYPE_FIXED_AMOUNT = 'FIXED_AMOUNT'
    DISCOUNT_TYPES = [
        (DISCOUNT_TYPE_PERCENTAGE, 'Percentage'),
        (DISCOUNT_TYPE_FIXED_AMOUNT, 'Fixed Amount'),
    ]
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2) #PERCENTAGE 쿠폰은 소수점으로 관리 0.2 = 20%
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self): # 쿠폰이 유효한지 검사
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    def get_discounted_amount(self, amount): # 쿠폰 적용시 사용되는 로직
        if self.discount_type == self.DISCOUNT_TYPE_PERCENTAGE:
            return amount - amount * self.discount_value
        else:
            return amount - self.discount_value


class UserCoupon(models.Model): # 유저가 가지고 있는 쿠폰
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    used_date = models.DateTimeField(null=True, blank=True)

class Transaction(models.Model): # 결제 내역
    TRANSACTION_TYPE_CHARGE = 'CHARGE' # 선불 충전
    TRANSACTION_TYPE_PAYMENT = 'PAYMENT' # 후불 결제
    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPE_CHARGE, 'Charge'),
        (TRANSACTION_TYPE_PAYMENT, 'Payment'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField() # 유저가 입력한 금액(총 결제하려는 금액)
    used_balance = models.IntegerField(default=0, blank=True) # 결제시 유저가 사용한 잔고
    actual_amount = models.IntegerField(default=0, blank=True) # 실제 결제된 금액 = 유저가 입력한 금액 - 결제시 유저가 사용한 잔고 - 쿠폰
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)

    class Meta:
        ordering = ['-date']