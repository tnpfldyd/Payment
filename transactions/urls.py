from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('payment', PaymentMethodViewSet, basename='payment-method')
router.register('user-coupon', UserCouponViewSet, basename='user-coupon')
router.register('coupon', CouponViewSet, basename='coupon')
router.register('transaction', TransactionViewSet, basename='transaction')
urlpatterns = [
    path('', include(router.urls)),
]