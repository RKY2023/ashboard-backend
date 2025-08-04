from django.urls import path
from .views import ToppingListView

urlpatterns = [
    path('', ToppingListView.as_view(), name='topping-list'),
]