from django.urls import path, include
from .views import UserProfileView

urlpatterns = [
    path('', UserProfileView.as_view(), name='user-profile'),
]