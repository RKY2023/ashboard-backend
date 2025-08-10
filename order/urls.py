from django.urls import path
# from .views import OrderItemsListView, OrderListView
from .views import (
    OrderItemListCreateAPIView, OrderItemRetrieveUpdateDestroyAPIView, OrderListCreateAPIView, OrderRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    # Order Items
    path('order-items/', OrderItemListCreateAPIView.as_view()),
    path('order-items/<int:pk>/', OrderItemRetrieveUpdateDestroyAPIView.as_view()),

    # Orders
    path('', OrderListCreateAPIView.as_view()),
    path('<int:pk>/', OrderRetrieveUpdateDestroyAPIView.as_view()),
    # path('', OrderItemsListView.as_view(), name='order_items_list'),
    # path('<int:pk>/', OrderItemsListView.as_view(), name='order_item_detail'),
    # path('order', OrderListView.as_view(), name='order_list'),
    # path('order/<int:pk>/', OrderListView.as_view(), name='order_detail'),
]