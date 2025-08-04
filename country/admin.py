from django.contrib import admin
from country.models import Country, CountryDetail

# Register your models here.
admin.site.register(Country)
admin.site.register(CountryDetail)  # Assuming you have a CountryDetails model