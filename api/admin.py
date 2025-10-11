from django.contrib import admin

from django.contrib.auth import get_user_model
from .models import DeliveryRequest, Assignment, Payment, Tracking

User = get_user_model()
# Register the User model with custom admin if needed
admin.site.register(User)
admin.site.register(DeliveryRequest)    
admin.site.register(Assignment)
admin.site.register(Payment)
admin.site.register(Tracking)