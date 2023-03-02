from django.urls import path, include
from rest_framework import routers
from .views import PaymentMethodViewSet

router = routers.DefaultRouter()
router.register('', PaymentMethodViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]