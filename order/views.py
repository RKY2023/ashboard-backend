from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import OrderItem, Order
from .serializers import OrderItemSerializer, OrderSerializer
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

# -------------------- ORDER ITEMS --------------------
class OrderItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'product': ['exact'],
        'order': ['exact'],
        'quantity': ['exact', 'lt', 'gt'],
        # 'amount': ['exact', 'lt', 'gt'],
    }

class OrderItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


# -------------------- ORDERS --------------------
class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'order_date': ['exact', 'lte', 'gte'],
        'status': ['exact', 'icontains'],
        'vendor': ['exact'],
    }

class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer



# class OrderItemsListView(APIView):
#     def get(self, request, pk=None):
#         if pk:
#             try:
#                 item = OrderItem.objects.get(pk=pk)
#                 serializer = OrderItemSerializer(item)
#                 return Response({'message': 'success', 'item': serializer.data}, status=status.HTTP_200_OK)
#             except OrderItem.DoesNotExist:
#                 return Response({'message': 'Order Item not found'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             items = OrderItem.objects.all()
#             serializer = OrderItemSerializer(items, many=True)
#             return Response({'message': 'success', 'items': serializer.data}, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = OrderItemSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Order Item created successfully', 'item': serializer.data}, status=status.HTTP_201_CREATED)
#         return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         if not pk:
#             return Response({'message': 'Order Item ID is required for update'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             item = OrderItem.objects.get(pk=pk)
#             serializer = OrderItemSerializer(item, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'message': 'Order Item updated successfully', 'item': serializer.data}, status=status.HTTP_200_OK)
#             return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except OrderItem.DoesNotExist:
#             return Response({'message': 'Order Item not found'}, status=status.HTTP_404_NOT_FOUND)  
        
#     def delete(self, request, pk):
#         if not pk:
#             return Response({'message': 'Order Item ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             item = OrderItem.objects.get(pk=pk)
#             item.delete()
#             return Response({'message': 'Order Item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
#         except OrderItem.DoesNotExist:
#             return Response({'message': 'Order Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
# class OrderListView(APIView):
#     def get(self, request, pk=None):
#         if pk:
#             try:
#                 order = Order.objects.get(pk=pk)
#                 serializer = OrderSerializer(order)
#                 return Response({'message': 'success', 'order': serializer.data}, status=status.HTTP_200_OK)
#             except Order.DoesNotExist:
#                 return Response({'message': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             orders = Order.objects.all()
#             serializer = OrderSerializer(orders, many=True)
#             return Response({'message': 'success', 'orders': serializer.data}, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             purchase_order = serializer.save()
#             serializer = OrderSerializer(purchase_order)
#             return Response({'message': 'Purchase Order created successfully', 'order': serializer.data}, status=status.HTTP_201_CREATED)
#         return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#     def put(self, request, pk=None):
#         if not pk:
#             return Response({'message': 'Purchase Order ID required for update'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             order = Order.objects.get(pk=pk)
#             serializer = OrderSerializer(order, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'message': 'Purchase Order updated successfully', 'order': serializer.data})
#             return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Order.DoesNotExist:
#             return Response({'message': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)
#     def delete(self, request, pk=None):
#         if not pk:
#             return Response({'message': 'Purchase Order ID required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             order = Order.objects.get(pk=pk)
#             order.delete()
#             return Response({'message': 'Purchase O                rder deleted successfully'})
#         except Order.DoesNotExist:
#             return Response({'message': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)