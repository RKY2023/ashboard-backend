from django.db import models
from django.core.validators import EmailValidator
# Create your models here.
class Vendor(models.Model):
    vendor_name = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True, validators=[
        EmailValidator(message="Enter a valid email address.")
    ])

    def __str__(self):
        return self.vendor_name

    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'