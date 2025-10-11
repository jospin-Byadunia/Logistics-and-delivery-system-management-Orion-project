from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DeliveryRequest, Assignment, Payment, Tracking

User = get_user_model()

# --------------------
# User Serializer
# --------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'address', 'vehicle_number']
        read_only_fields = ['id']


# --------------------
# DeliveryRequest Serializer
# --------------------
class DeliveryRequestSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.CUSTOMER)
    )

    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'customer', 'pickup_address', 'dropoff_address',
            'pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng',
            'distance_km', 'price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'distance_km', 'price', 'created_at', 'updated_at']


# --------------------
# Assignment Serializer
# --------------------
class AssignmentSerializer(serializers.ModelSerializer):
    driver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.DRIVER)
    )
    delivery_request = serializers.PrimaryKeyRelatedField(queryset=DeliveryRequest.objects.all())

    class Meta:
        model = Assignment
        fields = ['id', 'driver', 'delivery_request', 'assigned_at', 'accepted']
        read_only_fields = ['id', 'assigned_at']


# --------------------
# Payment Serializer
# --------------------
class PaymentSerializer(serializers.ModelSerializer):
    delivery_request = serializers.PrimaryKeyRelatedField(queryset=DeliveryRequest.objects.all())

    class Meta:
        model = Payment
        fields = [
            'id', 'delivery_request', 'amount', 'currency',
            'payment_method', 'transaction_id', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status', 'transaction_id']


# --------------------
# Tracking Serializer
# --------------------
class TrackingSerializer(serializers.ModelSerializer):
    driver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.DRIVER)
    )
    delivery_request = serializers.PrimaryKeyRelatedField(queryset=DeliveryRequest.objects.all())

    class Meta:
        model = Tracking
        fields = ['id', 'delivery_request', 'driver', 'latitude', 'longitude', 'timestamp']
        read_only_fields = ['id', 'timestamp']
