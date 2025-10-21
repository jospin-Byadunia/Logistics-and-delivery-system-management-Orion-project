from rest_framework.permissions import BasePermission
from api.models import Assignment

class DeliveryRequestPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True
        if user.role == 'CUSTOMER' and obj.customer == user:
            return True
        if user.role == 'DRIVER':
            return Assignment.objects.filter(driver=user, delivery_request=obj).exists()
        return False
