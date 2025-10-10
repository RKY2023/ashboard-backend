from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Email is mandatory and unique
    Username is optional but will be auto-generated if not provided
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirm Password"
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Optional username. If not provided, will be auto-generated from email"
    )

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password2',
            'username',
            'mobile',
            'first_name',
            'last_name',
            'date_of_birth',
            'address'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'mobile': {'required': False},
            'date_of_birth': {'required': False},
            'address': {'required': False}
        }

    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def validate_email(self, value):
        """Ensure email is unique and properly formatted"""
        if not value:
            raise serializers.ValidationError("Email is required.")

        # Normalize email
        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Ensure username is unique if provided"""
        # Username is optional, but if provided must be unique
        if value:
            value = value.strip()
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_mobile(self, value):
        """Ensure mobile is unique if provided"""
        if value and User.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("A user with this mobile number already exists.")
        return value

    def create(self, validated_data):
        """Create user with hashed password and create user profile"""
        from userprofile.models import UserProfile

        # Remove password2 as it's not needed for user creation
        validated_data.pop('password2')

        # Extract username for profile if provided
        profile_username = validated_data.get('username', None)

        # Create user with create_user to properly hash password
        # If username not provided, it will be auto-generated in User.save()
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data.get('username', None),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            mobile=validated_data.get('mobile', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
            address=validated_data.get('address', '')
        )

        # Create UserProfile with username
        UserProfile.objects.create(
            user=user,
            username=profile_username or user.username,
            date_of_birth=validated_data.get('date_of_birth', None),
            location=validated_data.get('address', '')
        )

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Supports login with email or mobile
    """
    email = serializers.EmailField(
        required=True,
        help_text="Email address or mobile number"
    )
    password = serializers.CharField(
        max_length=128,
        write_only=True,
        style={'input_type': 'password'}
    )


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()   