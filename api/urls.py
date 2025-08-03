from django.urls import path
from . import views
from .views import ApiHomeView
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    # path('', views.api_home, name='api-home'),
    path('', csrf_exempt(ApiHomeView.as_view()), name='api-home'),
]