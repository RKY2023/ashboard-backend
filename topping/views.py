# from django.shortcuts import render
from .models import Topping
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ToppingSerializer
# from django.views import View
# Create your views here. DRF rather than Django class-based view
class ToppingListView(APIView):
    serializer_class = ToppingSerializer

    def get(self, request):
        toppings = Topping.objects.all()
        data = list(toppings.values())
        return Response({"message": "success", "toppings": data}) 