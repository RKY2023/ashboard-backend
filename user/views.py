from django.shortcuts import render
from rest_framework.views import APIView as ApiView
from rest_framework.response import Response
from .models import User
# Create your views here.
class UserView(ApiView):
    def get(self, request):
        users = User.objects.all()
        data = list(users.values())
        return render(request, 'user/user_list.html', {'users': data})
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if username and email and password:
            user = User.objects.create(username=username, email=email, password=password)
            return Response({'message': 'User created successfully', 'user_id': user.id})
        return Response({'error': 'Invalid data'}, status=400)