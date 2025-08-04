from django.db import models

# Create your models here.
class Topping(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_vegetarian = models.BooleanField(default=False)
    parent_topping = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, related_name='child_toppings')
    # parent_topping = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, related_name='child_toppings')
    
    def __str__(self):
        return self.name