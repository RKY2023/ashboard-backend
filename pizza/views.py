from django.shortcuts import render
from .models import Pizza
from django.views import View
from django.http import JsonResponse

# Create your views here.
class PizzaListView(View):
    def get(self, request):
        pizzas = Pizza.objects.all()
        data = list(pizzas.values())
        return JsonResponse({"message": "success", "pizzas": data})