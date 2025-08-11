from django.urls import path, include
from .views import ProductViewSet, ProductInfoAPIView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    
    # path('', ProductListCreateAPIView.as_view(), name='product_list'),
    # path('<int:pk>/', ProductListCreateAPIView.as_view(), name='product_detail'),
    
    # path('', ProductAPIView.as_view(), name='product_list'),
    # path('<int:pk>/', ProductAPIView.as_view(), name='product_detail'),
    # path('add/', ProductAPIView.product_add, name='product_add'),
    # path('edit/<int:pk>/', ProductAPIView.product_edit, name='product_edit'),
    # path('delete/<int:pk>/', ProductAPIView.product_delete, name='product_delete'),
]