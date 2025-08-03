from django.urls import path
from . import views
from .views import StateView

urlpatterns = [
    # path('', StateView.as_view(), name='states' )
    path('', views.get, name='states'),
]