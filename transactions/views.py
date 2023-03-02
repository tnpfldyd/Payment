from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import PaymentMethod, UserCoupon, Coupon
from .serializers import PaymentMethodSerializer, CardSerializer, AccountSerializer, UserCouponSerializer, CouponSerializer
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