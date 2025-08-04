from django.urls import path
from .views import UserView

urlpatterns = [
    path('users/', UserView.as_view(), name='user-list'),
    # path('users/create/', UserView.as_view(), name='user-create'),
]