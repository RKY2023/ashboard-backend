from django.db import models
from django.core.validators import EmailValidator
from django.conf import settings
# Create your models here.
class Vendor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True, validators=[
        EmailValidator(message="Enter a valid email address.")
    ])

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'