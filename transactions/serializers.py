from rest_framework import serializers
from .models import PaymentMethod, Card, Account, Coupon, UserCoupon, Transaction
from accounts.serializers import BalanceSerializer


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_information = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = '__all__'

    def get_payment_information(self, obj):
        serializer = CardSerializer(obj.card) if obj.payment_type == 'CARD' else AccountSerializer(obj.account)
        return serializer.data

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    class Meta:
        model = UserCoupon
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    payment_method = PaymentMethodSerializer(read_only=True)
    coupon = CouponSerializer(read_only=True)
    balance = BalanceSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'