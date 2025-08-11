from django.db import models
from django.contrib.auth.models import User

# from django.contrib.admin import profile
from django.conf import settings
# Create your models here.
class UserProfile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    print('migration file created', User)

    def __str__(self):
        return self.user.username
