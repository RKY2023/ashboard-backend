from django.db import models

# Create your models here.
class Country(models.Model):
    country_name = models.CharField(max_length=100, verbose_name='Country Name', unique=True)
    country_code = models.CharField(max_length=20, verbose_name='Country Code')
    country_slug = models.SlugField(max_length=100, default="default-slug")
    country_description = models.TextField()
    # iso_code = models.CharField(max_length=3, default="XXX")
    continent = models.CharField(max_length=100, null=True)
    
    # class Meta:
    #     verbose_name = "Country"
    #     verbose_name_plural = "Countries"
    #     ordering = ['country_name']

    def __str__(self):
        return self.country_name
class OrdeyByNameDscCountry(Country):
    class Meta:
        verbose_name = "My Country"
        verbose_name_plural = "My Countries"
        ordering = ['-country_name']
        proxy = True  # This makes it a proxy model
        # abstract = False  # This is not an abstract model
    # def is_asian(self):
    #     return self.continent.lower() == 'asia'

    def __str__(self):
        return f"My Country: {self.country_name}"
class CountryDetail(models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)
    flag = models.ImageField(upload_to='flags/', null=True, blank=True)

    class Meta:
        verbose_name = "Country Detail"
        verbose_name_plural = "Country Details"

    def __str__(self):
        return f"Details for {self.country.country_name}"