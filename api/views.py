from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
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
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action


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
    permission_classes = [IsAuthenticated]

    @action(
        detail=True,
        methods=['patch'],
        url_path='accept',
        permission_classes=[IsAuthenticated]
    )
    def accept(self, request, pk=None):
        assignment = get_object_or_404(Assignment, pk=pk, driver=request.user)
        assignment.status = Assignment.ACCEPTED
        assignment.save()

        # Update delivery request status
        assignment.delivery_request.status = DeliveryRequest.IN_PROGRESS
        assignment.delivery_request.save()

        return Response({'detail': 'Assignment accepted successfully.'})

    @action(
        detail=True,
        methods=['patch'],
        url_path='reject',
        permission_classes=[IsAuthenticated]
    )
    def reject(self, request, pk=None):
        assignment = get_object_or_404(Assignment, pk=pk, driver=request.user)

        reason = request.data.get('reason')
        if not reason:
            return Response({'detail': 'Rejection reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark assignment as rejected
        assignment.status = Assignment.REJECTED
        assignment.rejection_reason = reason
        assignment.save()

        # Set delivery back to pending so it can be reassigned
        delivery = assignment.delivery_request
        delivery.status = DeliveryRequest.PENDING
        delivery.save()

        return Response({'detail': 'Assignment rejected successfully. Delivery is now available for reassignment.'})

    @action(
        detail=False,
        methods=['post'],
        url_path=r'(?P<pk>\d+)/assign',
        permission_classes=[IsAdminUser]
    )
    def assign_driver(self, request, pk=None):
        """Admin manually assigns a driver to a delivery request."""
        delivery = get_object_or_404(DeliveryRequest, pk=pk)

        # Check if delivery is available for assignment
        if delivery.status not in [DeliveryRequest.PENDING, DeliveryRequest.CANCELLED]:
            return Response({'detail': 'This delivery is not available for assignment.'},
                            status=status.HTTP_400_BAD_REQUEST)

        driver_id = request.data.get('driver_id')
        if not driver_id:
            return Response({'detail': 'Driver ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create assignment
        assignment = Assignment.objects.create(
            delivery_request=delivery,
            driver_id=driver_id
        )

        delivery.status = DeliveryRequest.ASSIGNED
        delivery.save()

        return Response(AssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)
    @action(
    detail=True,
    methods=['patch'],
    url_path='complete',
    permission_classes=[IsAuthenticated]
)
    def complete(self, request, pk=None):
        """
        Driver marks the delivery as completed.
        """
        assignment = get_object_or_404(Assignment, pk=pk)

        # Only the assigned driver can complete
        if request.user != assignment.driver:
            return Response({'detail': 'You are not authorized to complete this assignment.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Only accepted assignments can be completed
        if assignment.status != Assignment.ACCEPTED:
            return Response({'detail': 'Only accepted assignments can be completed.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update assignment status
        assignment.status = Assignment.ACCEPTED  # keep as accepted or optionally create COMPLETED in Assignment
        assignment.save()

        # Update delivery request status
        delivery = assignment.delivery_request
        delivery.status = DeliveryRequest.COMPLETED
        delivery.save()

        return Response({'detail': 'Delivery marked as completed successfully.'}, status=status.HTTP_200_OK)


# --------------------
# Payment ViewSet
# --------------------
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        delivery_request_id = request.data.get('delivery_request')
        payment_method = request.data.get('payment_method')

        try:
            delivery_request = DeliveryRequest.objects.get(id=delivery_request_id)
        except DeliveryRequest.DoesNotExist:
            return Response({'error': 'Delivery request not found'}, status=status.HTTP_404_NOT_FOUND)

        amount = delivery_request.price
        if amount is None:
            return Response({'error': 'Delivery request price is not set'}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            delivery_request=delivery_request,
            amount=amount,
            payment_method=payment_method,
        )

        if payment_method in [Payment.CARD, Payment.MOBILE_MONEY]:
            # Here you integrate with Flutterwave or other payment API
            # Example: get payment link and return
            payment_link = f"https://pay.example.com/{payment.id}"  # placeholder
            return Response({'payment_id': payment.id, 'payment_link': payment_link})

        # Pay on delivery option
        return Response({'payment_id': payment.id, 'message': 'Payment will be collected on delivery'})

    def update_status(self, request, pk=None):
        """ Endpoint to update payment status after webhook """
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        status_ = request.data.get('status')
        transaction_id = request.data.get('transaction_id')
        if status_ not in [Payment.PENDING, Payment.SUCCESS, Payment.FAILED]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = status_
        if transaction_id:
            payment.transaction_id = transaction_id
        payment.save()

        # Mark delivery request as paid if successful
        if status_ == Payment.SUCCESS:
            payment.delivery_request.is_paid = True
            payment.delivery_request.save()

        return Response({'message': 'Payment status updated'})


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