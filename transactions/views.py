from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import PaymentMethod, Card, Account
from .serializers import PaymentMethodSerializer, CardSerializer, AccountSerializer


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