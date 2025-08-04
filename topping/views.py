# from django.shortcuts import render
from .models import Topping
from rest_framework.response import Response
from rest_framework.views import APIView
# from django.views import View
# Create your views here. DRF rather than Django class-based view
class ToppingListView(APIView):
    def get(self, request):
        toppings = Topping.objects.all()
        data = list(toppings.values())
        return Response({"message": "success", "toppings": data}) 