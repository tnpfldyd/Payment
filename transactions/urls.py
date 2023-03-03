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

# payment api (결제 정보 등록)
# base_url/api/transactions/payment/
# GET요청시 = 사용자가 등록한 결제 정보 
# POST요청시(등록) 예시
# 카드 = {
#     "payment_method_type": "CARD",
#     "card_company": "BC",
#     "card_number": "1234123412341234",
#     "expiry_month": 10,
#     "expiry_year": 2027,
#     "cvc": 123,
#     "user": user.pk
# }
# 계좌 = {
#     "payment_method_type": "ACCOUNT",
#     "bank_name": "IBK",
#     "account_number": "계좌번호",
#     "user": user.pk
# }
# DELETE 요청시
# base_url/api/transactions/payment/payment:pk/

# coupon api 쿠폰 상세보기 (필요시) - 시리얼라이저에 기본적으로 들어가 있으나 혹시나 필요시 사용
# base_url/api/transactions/coupon/coupon:pk/
# GET 요청만 가능. POST, PUT, DELETE는 admin만 가능


# user-coupon api 쿠폰 등록(쿠폰번호를 가지고 유저가 등록할 때 사용)
# base_url/api/transactions/user-coupon/
# GET요청시 = 사용자가 가지고 있는 쿠폰 (사용 하지 않은 쿠폰) 사용한 것도 필요시 views.py 50번줄 user=False 삭제
# POST요청시(쿠폰등록) 예시
# {
#     "coupon_code": "admin에서 발급한 코드", 
#     "user": user.pk
#     }


# transaction api 결제 정보
# base_url/api/transactions/transaction/
# GET요청시 = 사용자가 결제한 목록 출력 (파라미터로 ?transaction_type=CHARGE or PAYMENT 가능)
# POST요청시 예시
# 선불 충전시 use_balance 입력 금지.
# 선불 충전 = {
#     "amount": 50000,
#     "payment_id"(등록한 결제정보 pk): 2, 등록한 결제정보 말고 새로운 결제정보로 진행시 입력하지 않고 진행 or 0 or null
#     "coupon_id": 3, 쿠폰 미 사용시 입력하지 않고 진행 or 0 or null
#     "user": user.pk 
# }

# 후불 결시시 use_balance 필수 입력.
# 후불 결제 = {
#     "amount": 50000,
#     "payment_id"(등록한 결제정보 pk): 2, 등록한 결제정보 말고 새로운 결제정보로 진행시 입력하지 않고 진행 or 0 or null
#     "coupon_id": 3, 쿠폰 미 사용시 입력하지 않고 진행 or 0 or null
#     "user": user.pk,
#     "use_balance": 30000 or 0 입력 use_balance의 존재 유무에 따라 충전과 결제가 나뉘니 잔고를 사용하지 않아도 필수로 값 입력
# }
