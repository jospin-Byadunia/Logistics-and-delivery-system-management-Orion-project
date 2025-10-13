from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    # Define role choices
    ADMIN = 'ADMIN'
    DRIVER = 'DRIVER'
    CUSTOMER = 'CUSTOMER'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (DRIVER, 'Driver'),
        (CUSTOMER, 'Customer'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CUSTOMER
    )
    
    phone_number = models.CharField(max_length=15)
    
    # Optional fields
    address = models.TextField(blank=True, null=True)  # for customers
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # for drivers

    def __str__(self):
        return f"{self.username} ({self.role})"


class DeliveryRequest(models.Model):
    # Status choices
    PENDING = 'PENDING'
    ASSIGNED = 'ASSIGNED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ASSIGNED, 'Assigned'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CUSTOMER'},  # Ensures only customers can be assigned
        related_name='delivery_requests'
    )

    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()
    
    distance_km = models.FloatField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"DeliveryRequest #{self.id} - {self.customer.username} ({self.status})"


class Assignment(models.Model):
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DRIVER'},  # Ensures only drivers can be assigned
        related_name='assignments'
    )

    delivery_request = models.ForeignKey(
        'DeliveryRequest',
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Assignment #{self.id} - Driver: {self.driver.username} for DeliveryRequest #{self.delivery_request.id}"
    
    
class Payment(models.Model):
    # Payment method choices
    CARD = 'CARD'
    MOBILE_MONEY = 'MOBILE_MONEY'
    PAYPAL = 'PAYPAL'
    
    PAYMENT_METHOD_CHOICES = [
        (CARD, 'Card'),
        (MOBILE_MONEY, 'Mobile Money'),
        (PAYPAL, 'PayPal'),
    ]

    # Payment status choices
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]

    delivery_request = models.ForeignKey(
        'DeliveryRequest',
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.delivery_request.id} ({self.status})"
    
    
class Tracking(models.Model):
    delivery_request = models.ForeignKey(
        'DeliveryRequest',
        on_delete=models.CASCADE,
        related_name='tracking_updates'
    )

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DRIVER'},
        related_name='tracking_updates'
    )

    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tracking Update: Delivery #{self.delivery_request.id} by {self.driver.username} at {self.timestamp}"