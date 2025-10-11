from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    DeliveryRequestViewSet,
    AssignmentViewSet,
    PaymentViewSet,
    TrackingViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'delivery-requests', DeliveryRequestViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'tracking', TrackingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
