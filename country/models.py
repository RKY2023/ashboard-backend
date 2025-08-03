from django.db import models

# Create your models here.
class Country(models.Model):
    country_name = models.CharField(max_length=100, verbose_name='Country Name', unique=True)
    country_code = models.CharField(max_length=20, verbose_name='Country Code')
    country_slug = models.SlugField(max_length=100, default="default-slug")
    country_description = models.TextField()

    def __str__(self):
        return self.country_name