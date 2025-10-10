from django.urls import path
from .views import UserView, LoginView, LogoutView, RegisterView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserView, basename='user')
urlpatterns = [
    path('', UserView.as_view(), name='user-list'),
    path('users/', UserView.as_view(), name='user-list'),
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
]