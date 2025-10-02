from django.shortcuts import render
from django.views import View
from rest_framework.response import Response
from rest_framework.decorators import api_view
from state.models import State
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from .serializers import StateSerializer

# Create your views here.
class StateView(View):
    def get(self, request):
        states = State.objects.all()
        data = list(states.values())
        return JsonResponse({"message": "success1", "data": data})

@extend_schema(responses=StateSerializer(many=True))
@api_view(['GET'])
def get(request):
    states = State.objects.all()
    data = list(states.values())
    return Response({"message": "success2", "data": data}    )
    