from django.shortcuts import render
from rest_framework.views import APIView as ApiView
from rest_framework.response import Response
from .models import User
from .serializers import UserLoginSerializer, UserListSerializer, UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework import status
from .utils import get_tokens_for_user
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiExample
# Create your views here.
class UserView(ApiView):
    serializer_class = UserListSerializer

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

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(ApiView):
    """
    API endpoint for user registration
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register New User",
        description="Create a new user account with username, email, and password. Returns user details and JWT tokens upon successful registration.",
        request=UserRegistrationSerializer,
        examples=[
            OpenApiExample(
                'Registration with Username',
                value={
                    'email': 'john@example.com',
                    'password': 'SecurePass123!',
                    'password2': 'SecurePass123!',
                    'username': 'johndoe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'mobile': '+1234567890',
                    'address': '123 Main St, City, Country'
                },
                request_only=True
            ),
            OpenApiExample(
                'Registration without Username (auto-generated)',
                value={
                    'email': 'jane@example.com',
                    'password': 'SecurePass123!',
                    'password2': 'SecurePass123!',
                    'first_name': 'Jane',
                    'last_name': 'Doe'
                },
                request_only=True
            ),
            OpenApiExample(
                'Success Response',
                value={
                    'message': 'User registered successfully',
                    'user': {
                        'id': 1,
                        'username': 'johndoe',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'mobile': '+1234567890'
                    },
                    'tokens': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                    }
                },
                response_only=True,
                status_codes=['201']
            )
        ],
        tags=['Authentication']
    )
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Generate tokens for the new user
            tokens = get_tokens_for_user(user)

            # Prepare user data for response
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mobile': user.mobile,
                'date_of_birth': user.date_of_birth,
                'address': user.address
            }

            return Response({
                'message': 'User registered successfully',
                'user': user_data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(ApiView):
    """
    API endpoint for user login
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="User Login",
        description="Authenticate user with email/mobile and password. Returns JWT tokens for authenticated requests.",
        request=UserLoginSerializer,
        examples=[
            OpenApiExample(
                'Login with Email',
                value={
                    'email': 'john@example.com',
                    'password': 'SecurePass123!'
                },
                request_only=True
            ),
            OpenApiExample(
                'Login with Mobile',
                value={
                    'email': '+1234567890',
                    'password': 'SecurePass123!'
                },
                request_only=True
            ),
            OpenApiExample(
                'Success Response',
                value={
                    'msg': 'Logged in successfully',
                    'token': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                    }
                },
                response_only=True,
                status_codes=['200']
            )
        ],
        tags=['Authentication']
    )
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email_or_mobile = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            # Get the user by email or mobile
            user = None
            UserModel = get_user_model()

            try:
                # Try to find the user by email or mobile
                if '@' in email_or_mobile:
                    # Login with email
                    user = UserModel.objects.get(email=email_or_mobile.lower())
                else:
                    # Login with mobile
                    user = UserModel.objects.get(mobile=email_or_mobile)

                # Verify password
                if user and user.check_password(password):
                    token = get_tokens_for_user(user)

                    # Return user info along with tokens
                    return Response({
                        'msg': 'Logged in successfully',
                        'token': token,
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                        }
                    }, status=status.HTTP_200_OK)

            except UserModel.DoesNotExist:
                pass

            return Response(
                {'errors': {'non_field_errors': ['Email/Mobile or Password is not valid']}},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(ApiView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        # In a real application, you would handle session or token invalidation here
        return Response({'message': 'Logout successful'})