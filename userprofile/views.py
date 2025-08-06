from django.shortcuts import render
# from django.contrib.admin import profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from userprofile.models import UserProfile
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
# Create your views here.
class UserProfileView(APIView):
    def get(self, request, format=None):
        user = request.user
        # with open("request_log.json", "a") as f:
        #     f.write(json.dumps(request) + "\n")
        # group = Group.objects.get(name='Editors')
        group = Group.objects.all()
        perm = Permission.objects.get(codename='change_user', content_type__app_label='auth')
        # group.permissions.remove(perm)
        print('User Profile:', user,str(get_user_model()), 'profile:',group,'perm', perm)

        user.user_permissions.remove(perm)
        if user.is_authenticated:
            profile_data = {
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'is_authenticated': user.is_authenticated,
                'date_joined': user.date_joined,
                'is_anynonymous': user.is_anonymous,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'last_login': user.last_login,
                'id': user.id,
                'all_permissions': user.get_all_permissions(),
                'user_permissions': user.get_user_permissions(),
                'groups': user.get_group_permissions(),
                'has_perm': user.has_perms(['auth.change_user']),
                'has_module_perm': user.has_module_perms(['austh']),
                'bio': user.userprofile.bio if hasattr(user, 'userprofile') else '',
                'location': user.userprofile.location if hasattr(user, 'userprofile') else '',
                'date_of_birth': user.userprofile.date_of_birth if hasattr(user, 'userprofile') else ''
            }
            return Response(profile_data, status=status.HTTP_200_OK)
        return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)