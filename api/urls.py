from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    DeliveryRequestViewSet,
    AssignmentViewSet,
    PaymentViewSet,
    TrackingViewSet, RegisterViewSet, LogoutView, ForgotPasswordView, CustomTokenObtainPairView, ProfileViewSet
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'delivery-requests', DeliveryRequestViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'tracking', TrackingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/',RegisterViewSet.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('profile/', ProfileViewSet.as_view({'get': 'list'}), name='profile'),
    #update profile can be added similarly
    path('profile/<int:pk>/', ProfileViewSet.as_view({'patch': 'me'}), name='update-profile'),
    
        
     # Custom routes for assignment actions
    path('deliveries/<int:pk>/assign/', AssignmentViewSet.as_view({'post': 'assign_driver'}), name='assign-driver'),
    path('assignments/<int:pk>/accept/', AssignmentViewSet.as_view({'patch': 'accept'}), name='accept-assignment'),
    path('assignments/<int:pk>/reject/', AssignmentViewSet.as_view({'patch': 'reject'}), name='reject-assignment'),
    path('assignments/<int:pk>/complete/', AssignmentViewSet.as_view({'patch': 'complete'}), name='complete-assignment'),
]
