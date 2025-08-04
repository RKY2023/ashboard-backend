from django.db import models
from topping.models import Topping

# Create your models here.
class Pizza(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_vegetarian = models.BooleanField(default=False)
    toppings = models.ManyToManyField(Topping, blank=True)
    
    def __str__(self):
        return self.name
