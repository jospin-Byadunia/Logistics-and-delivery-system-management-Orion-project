from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    DeliveryRequestViewSet,
    AssignmentViewSet,
    PaymentViewSet,
    TrackingViewSet, RegisterViewSet, LogoutView, ForgotPasswordView, CustomTokenObtainPairView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'delivery-requests', DeliveryRequestViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'tracking', TrackingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/',RegisterViewSet.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
]
