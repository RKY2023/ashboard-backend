from django.shortcuts import render
from rest_framework.views import APIView as ApiView
from rest_framework.response import Response
from .models import User
from .serializers import UserLoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework import status
from .utils import get_tokens_for_user
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

class LoginView(ApiView):
    serializer = UserLoginSerializer
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # email = serializer.validated_data.get('email')

            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            
            # Get the user by email or mobile
            user = None
            UserModel = get_user_model()
            print(user, password, username, '----')
            try:
                # Try to find the user by email or mobile
                if '@' in username:
                    user = UserModel.objects.get(email=username)
                else:
                    user = UserModel.objects.get(mobile=username)
                print(user, password, username, '----')
                # Verify password
                if user.check_password(password):
                    token = get_tokens_for_user(user)
                    return Response({'msg': 'Logged in successfully', 'token': token}, status=status.HTTP_200_OK)
                else:
                    user = None
            except UserModel.DoesNotExist:
                pass
            
            return Response(
                {'errors': {'non_field_errors': ['Email/Mobile or Password is not valid']}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(ApiView):
    def post(self, request):
        # In a real application, you would handle session or token invalidation here
        return Response({'message': 'Logout successful'})