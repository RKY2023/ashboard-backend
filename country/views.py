from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from country.models import Country, OrdeyByNameDscCountry
# Create your views here.

@api_view(['GET'])
def get_country(request):
    if request.method == 'GET':
        countries = OrdeyByNameDscCountry.objects.all()
        data = list(countries.values())
        return Response({"message": "success", "data": data})
    elif request.method == 'POST':
        country_name = request.data.get('country_name')
        country_code = request.data.get('country_code')
        country_slug = request.data.get('country_slug')
        country_description = request.data.get('country_description')
        country_data = Country(
            country_name=country_name,
            country_code=country_code,
            country_slug=country_slug,
            country_description=country_description
        )
        country_data.save()
        return Response({"message": "success", "data": {"id": country_data.id, "country_name": country_data.country_name}})
    else:
        return Response({"message": "fail", "error": "Invalid request method"})
        