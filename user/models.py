from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=150,unique=True,null=True,blank=True)
    mobile = models.CharField(max_length=15,blank=True , null=True, validators=[
            RegexValidator(
                regex=r'^\+?\d{0,3}?\d{9,15}$',
                message="Phone no must be in 10 digits. Add country code if needed.",
            ),
        ])
    date_of_birth = models.DateField(blank=True,null=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_user = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.PROTECT, related_name='created_by_parent', blank=True, null=True, default=None)
    address = models.CharField(max_length=500,blank=True,null=True)
    mobile_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'