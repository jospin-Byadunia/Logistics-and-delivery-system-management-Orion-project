from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DeliveryRequest, Assignment, Payment, Tracking
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
User = get_user_model()

# --------------------
# User Serializer
# --------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'role',
            'phone_number',
            'address',
            'vehicle_number'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


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
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    delivery_request_id = serializers.IntegerField(source='delivery_request.id', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'driver', 'driver_name', 'delivery_request', 'delivery_request_id',
            'assigned_at', 'status', 'rejection_reason'
        ]
        read_only_fields = ['assigned_at', 'status', 'rejection_reason']

# --------------------
# Payment Serializer
# --------------------
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'delivery_request', 'amount', 'currency', 'payment_method', 'transaction_id', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'transaction_id', 'created_at']

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        return payment


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

# --------------------
# Auth Serializer
# --------------------


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2','role', 'phone_number', 'address', 'vehicle_number')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.DictField(read_only=True)

    def validate(self, attrs):
        login = attrs.get('username')
        password = attrs.get('password')

        # Try username first
        user = None
        try:
            u = User.objects.get(username=login)
            if u.check_password(password):
                user = u
        except User.DoesNotExist:
            try:
                u = User.objects.get(email=login)
                if u.check_password(password):
                    user = u
            except User.DoesNotExist:
                user = None

        if user is None:
            raise serializers.ValidationError("Invalid username/email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        # Generate tokens manually
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }
        
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError("Invalid or expired token")
        

# For password reset (not fully implemented)
# class PasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("User with this email does not exist.")
#         return value

#     def save(self):
#         email = self.validated_data['email']
#         user = User.objects.get(email=email)
#         # Here you would generate a password reset link/token and send it via email
#         # For simplicity, we'll just generate a token
#         token = default_token_generator.make_token(user)
#         # In a real application, send the token to the user's email
#         return token