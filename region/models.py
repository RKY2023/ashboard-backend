from django.db import models
from state.models import State

# Create your models here.
class Region(models.Model):
    region_name = models.CharField(max_length=100)
    region_code = models.CharField(max_length=20, unique=True)
    region_slug = models.SlugField(max_length=100, default="default-slug")
    region_description = models.TextField()
    state = models.ForeignKey(State, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.region_name