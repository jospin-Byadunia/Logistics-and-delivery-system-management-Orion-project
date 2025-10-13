from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.crypto import get_random_string
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import DeliveryRequest, Assignment, Payment, Tracking
from .serializers import (
    UserSerializer,
    DeliveryRequestSerializer,
    AssignmentSerializer,
    PaymentSerializer,
    TrackingSerializer, RegisterSerializer, CustomTokenObtainPairSerializer, LogoutSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail


User = get_user_model()



# --------------------
# User ViewSet
# --------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':  # registration
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self): # Optionally filter by role
        role = self.request.query_params.get('role') 
        if role: 
            return User.objects.filter(role=role) 
        return User.objects.all()


# --------------------
# DeliveryRequest ViewSet
# --------------------
class DeliveryRequestViewSet(viewsets.ModelViewSet):
    queryset = DeliveryRequest.objects.all()
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the customer
        serializer.save(customer=self.request.user)


# --------------------
# Assignment ViewSet
# --------------------
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]


# --------------------
# Payment ViewSet
# --------------------
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


# --------------------
# Tracking ViewSet
# --------------------
class TrackingViewSet(viewsets.ModelViewSet):
    queryset = Tracking.objects.all()
    serializer_class = TrackingSerializer
    permission_classes = [permissions.IsAuthenticated]


# --------------------
# Auth Views
# --------------------
class RegisterViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            temp_password = get_random_string(8)
            user.set_password(temp_password)
            user.save()
            send_mail(
                "Password Reset",
                f"Your temporary password is: {temp_password}",
                "noreply@orion.com",
                [email],
                fail_silently=False,
            )
            return Response({"message": "Temporary password sent to your email."})
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer