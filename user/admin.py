from django.contrib import admin
from .models import User
# Register your models here.
admin.site.register(User)  # Assuming User model is imported from user.models