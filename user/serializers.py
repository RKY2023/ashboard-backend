from rest_framework import serializers
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    class Meta:
        model = User
        fields = ['username','password']
        
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()   