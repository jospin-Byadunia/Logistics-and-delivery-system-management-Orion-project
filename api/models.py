from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from geopy.distance import geodesic


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
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    HOUSEHOLD_ITEMS = 'HOUSEHOLD_ITEMS'
    OFFICE_EQUIPMENT = 'OFFICE_EQUIPMENT'
    PARCEL = 'PARCEL'
    FRAGILE = 'FRAGILE'
    FOOD = 'FOOD'
    OTHER = 'OTHER'

    PACKAGE_TYPE_CHOICES = [
        (HOUSEHOLD_ITEMS, 'Household Items'),
        (OFFICE_EQUIPMENT, 'Office Equipment'),
        (PARCEL, 'Parcel'),
        (FRAGILE, 'Fragile'),
        (FOOD, 'Food'),
        (OTHER, 'Other'),
    ]

    package_type = models.CharField(
        max_length=30,
        choices=PACKAGE_TYPE_CHOICES,
        default=PARCEL
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.pickup_lat and self.pickup_lng and self.dropoff_lat and self.dropoff_lng:
            pickup = (self.pickup_lat, self.pickup_lng)
            dropoff = (self.dropoff_lat, self.dropoff_lng)
            self.distance_km = geodesic(pickup, dropoff).km
            self.price = round(self.distance_km * 1.5, 2)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"DeliveryRequest #{self.id} - {self.customer.username} ({self.status})"


class Assignment(models.Model):
    ASSIGNED = 'ASSIGNED'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (ASSIGNED, 'Assigned'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DRIVER'},
        related_name='assignments'
    )

    delivery_request = models.ForeignKey(
        'DeliveryRequest',
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ASSIGNED)
    rejection_reason = models.TextField(null=True, blank=True)

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