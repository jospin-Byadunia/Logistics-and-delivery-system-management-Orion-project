from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .models import DeliveryRequest, Assignment, Payment, Tracking
from .serializers import (
    UserSerializer,
    DeliveryRequestSerializer,
    AssignmentSerializer,
    PaymentSerializer,
    TrackingSerializer
)

User = get_user_model()

# --------------------
# User ViewSet
# --------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally filter by role
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
