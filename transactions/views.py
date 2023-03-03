from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import *
from .serializers import *
from datetime import datetime

class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer

    def get_queryset(self):
        user = self.request.user
        return PaymentMethod.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        payment_method_data = {'user': request.user.id, 'payment_type': request.data.get('payment_method_type')}
        payment_method_serializer = PaymentMethodSerializer(data=payment_method_data)
        payment_method_serializer.is_valid(raise_exception=True)
        payment_method = payment_method_serializer.save()
        serializer_class = CardSerializer if payment_method.payment_type == 'CARD' else AccountSerializer
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(payment_method=payment_method)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_queryset().get(pk=kwargs['pk'])
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CouponViewSet(viewsets.ViewSet):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()

    def retrieve(self, request, pk=None):
        try:
            coupon = Coupon.objects.get(pk=pk)
        except Coupon.DoesNotExist:
            return Response({'error': '해당 쿠폰이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CouponSerializer(coupon)
        return Response(serializer.data)
    
class UserCouponViewSet(viewsets.ViewSet):
    serializer_class = UserCouponSerializer

    def list(self, request):
        user = request.user
        user_coupons = UserCoupon.objects.filter(user=user, used=False)
        serializer = UserCouponSerializer(user_coupons, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        coupon_code = request.data.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True,
                                         start_date__lte=datetime.now(),
                                         end_date__gte=datetime.now())
        except Coupon.DoesNotExist:
            return Response({'error': '만료되거나 존재하지 않는 쿠폰입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            UserCoupon.objects.get(user=user, coupon=coupon)
            return Response({'error': '이미 사용한 쿠폰입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except UserCoupon.DoesNotExist:
            pass
        user_coupon = UserCoupon.objects.create(user=user, coupon=coupon)
        serializer = UserCouponSerializer(user_coupon)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def api_PG(amount, payment_id): # PG 결제가 실행되는 로직입니다. 테스트 하기 위해 임시로 작성해두었습니다.
    if not amount: # 결제할 금액이 없을땐 결제 로직 실행 없이 바로 종료.
        return True
    if payment_id:
        payment = PaymentMethod.objects.get(id=payment_id)
    return True

class TransactionViewSet(viewsets.ViewSet):

    def list(self, request):
        user = request.user
        transaction_type = request.query_params.get('transaction_type')
        payments = Transaction.objects.filter(user=user)
        if transaction_type:
            payments = payments.filter(transaction_type=transaction_type.upper())
        serializer = TransactionSerializer(payments, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        data = request.data # 전송받은 데이터
        user = request.user # 유저
        user_balance = user.balance # 유저의 지갑
        amount = data.get('amount') # 유저가 총 결제하려는 금액
        
        if not amount:
            return Response({'success': False, 'message': '결제할 금액이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        actual_amount = amount
        use_balance = 0
        if data.get('use_balance'): # 충전 시에는 data에 use_balance 를 담지 않고 결제 시에는 담는 식으로 구현했습니다.
            use_balance = data['use_balance'] # 유저가 사용하려는 잔고
            
            if use_balance > amount: # 잔고가 결제하려는 금액보다 더 많을 때
                use_balance = amount

            if user_balance.balance < use_balance:
                return Response({'success': False, 'message': '잔고가 부족합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_balance.balance -= use_balance
            actual_amount -= use_balance
        else: # use_balance란 데이터가 존재하지 않을 시에는 충전이 되도록 구현했습니다..
            user_balance.balance += amount
        
        coupon_id = data.get('coupon_id')
        coupon = None
        if coupon_id:
            try:
                user_coupon = UserCoupon.objects.get(id=coupon_id)
                
                if user_coupon.used:
                    return Response({'success': False, 'message': '이미 사용한 쿠폰입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
                coupon = user_coupon.coupon
                
                if not coupon.is_valid():
                    return Response({'success': False, 'message': '사용할 수 없는 쿠폰입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
                actual_amount = coupon.get_discounted_amount(actual_amount) # 쿠폰 적용된 금액
                user_coupon.used = True # 결제가 되기 전엔 유저의 지갑과 쿠폰은 저장하지 않았습니다.
            
            except UserCoupon.DoesNotExist:
                return Response({'success': False, 'message': '사용자에게 없는 쿠폰입니다.'}, status=status.HTTP_400_BAD_REQUEST)
       
        payment_id = data.get('payment_id')
        payment = None
        if payment_id:
            payment = PaymentMethod.objects.get(id=payment_id)
            if payment.user != user:
                return Response({'success': False, 'message': '결제 등록한 정보와 불일치 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if actual_amount < 0:
            actual_amount = 0

        if not api_PG(actual_amount, payment_id): # PG 결제가 실패했을 경우
            return Response({'success': False, 'message': '결제에 실패하였습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        transaction = Transaction.objects.create(
            user = user,
            amount = amount,
            coupon = coupon,
            used_balance = -use_balance,
            actual_amount = actual_amount,
            transaction_type='PAYMENT' if data.get('use_balance') else 'CHARGE',
            payment_method=payment,
        )
        user_balance.save() # 결제가 성공되면 그때 유저의 정보와 쿠폰의 데이터를 저장합니다.
        if coupon_id: # 쿠폰이 있을 경우에만 쿠폰 저장
            user_coupon.save()
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
