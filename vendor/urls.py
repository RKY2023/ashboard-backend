from django.urls import path
from .views import VendorListCreateAPIView
urlpatterns = [
    path('', VendorListCreateAPIView.as_view(), name='vendor_list'),
    path('<int:pk>/', VendorListCreateAPIView.as_view(), name='vendor_detail'),
]