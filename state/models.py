from django.db import models
from country.models import Country

# Create your models here.
class State(models.Model):
    state_name = models.CharField(max_length=100)
    state_name = models.CharField(max_length=100, verbose_name='State Name', unique=True)
    state_code = models.CharField(max_length=20, verbose_name='State Code')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    def __str__(self):
        return self.state_name
