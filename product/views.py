from django.shortcuts import get_object_or_404
from product.models import Product
from django.http import JsonResponse, HttpResponse
from django.views import View
from rest_framework import serializers, status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name', 'product_code', 'selling_price']
        # fields = '__all__'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'product_code'
    # pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'id': ['exact', 'lt', 'gt'],
        'product_name': ['exact', 'icontains'],
        'product_code': ['exact', 'icontains'],
        'selling_price': ['exact', 'lt', 'gt'],
        'purchase_price': ['exact', 'lt', 'gt'],
    }
# class ProductListCreateAPIView(generics.ListCreateAPIView,
#                      generics.RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = {
#         'product_name': ['exact', 'icontains'],
#         'product_code': ['exact', 'icontains'],
#         'selling_price': ['exact', 'lt', 'gt'],
#         'purchase_price': ['exact', 'lt', 'gt'],
#     }
# class ProductAPIView(APIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = {
#         'product_name': ['exact', 'icontains'],
#         'product_code': ['exact', 'icontains'],
#         'selling_price': ['exact', 'lt', 'gt'],
#         'purchase_price': ['exact', 'lt', 'gt'],
#     }
    
#     def list(self, request, pk=None):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = self.get_serializer(product)
#         return Response({'message': 'success', 'product':serializer.data})

#     def retrieve(self, request, pk=None):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = self.get_serializer(product)
#         return Response({'message': 'success', 'product': serializer.data})

#     def update(self, request, pk=None):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = self.get_serializer(product, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'message': 'Product updated successfully', 'product': serializer.data})

#     def destroy(self, request, pk=None):
#         product = get_object_or_404(Product, pk=pk)
#         product.delete()
#         return Response({'message': 'Product deleted successfully'})


# class ProductAPIView(generics.ListAPIView):
#     # filterset_fields = {
#     #     'product_name': ['exact', 'icontains'],
#     #     'product_code': ['exact', 'icontains'],
#     #     'selling_price': ['exact', 'lt', 'gt'],
#     #     'purchase_price': ['exact', 'lt', 'gt'],
#     # }
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
#     filterset_fields = ('product_name', 'product_code', 'selling_price', 'purchase_price')
    

#     def get(self, request, pk=None):
#         if pk:
#             try:
#                 product = Product.objects.get(pk=pk)
#                 serializer = ProductSerializer(product)
#                 return Response({'message': 'success', 'product': serializer.data}, status=status.HTTP_200_OK)
#             except Product.DoesNotExist:
#                 return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             products = Product.objects.all()
#             serializer = ProductSerializer(products, many=True)
#             return Response({'message': 'success', 'products': serializer.data}, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Product added successfully', 'product': serializer.data}, status=status.HTTP_201_CREATED)
#         return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk=None):
#         if not pk:
#             return Response({'message': 'Product ID required for update'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             product = Product.objects.get(pk=pk)
#             serializer = ProductSerializer(product, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'message': 'Product updated successfully', 'product': serializer.data})
#             return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Product.DoesNotExist:
#             return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

#     def delete(self, request, pk=None):
#         if not pk:
#             return Response({'message': 'Product ID required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             product = Product.objects.get(pk=pk)
#             product.delete()
#             return Response({'message': 'Product deleted successfully'})
#         except Product.DoesNotExist:
#             return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

# class ProductView(View):
#     def product_list(request):
#         products = Product.objects.all()
#         products_data = list(products.values())
#         return JsonResponse({'message': 'success','products': products_data})

#     def product_detail(request, pk):
#         if Product.objects.filter(pk=pk).exists():
#             product = Product.objects.get(pk=pk)
#             product_data = ProductSerializer(product)
#             return JsonResponse({'message': 'success','product': product_data.data})
#         else:
#             return HttpResponse('Product not found', status=404)
#     @csrf_exempt
#     def product_add(request):
#         try:
#             product_name = request.POST.get('product_name')
#             product_code = request.POST.get('product_code')
#             selling_price = request.POST.get('selling_price')
#             purchase_price = request.POST.get('purchase_price')
#             if product_name and product_code and selling_price and purchase_price:
#                 product = Product.objects.create(
#                     product_name=product_name,
#                     product_code=product_code,
#                     selling_price=selling_price,
#                     purchase_price=purchase_price
#                 )
#                 return JsonResponse({'message': 'Product added successfully', 'product': str(product)})
#             else:
#                 return JsonResponse({'message': 'Invalid data'}, status=400)
#             pass
#         except Exception as e:
#             return JsonResponse({'message': 'Error adding product', 'error': str(e)}, status=500)
#     @csrf_exempt
#     def product_edit(request, pk):
#         try:
#             # print(f"Editing product with ID: {pk}", request.body)
#             # return JsonResponse({'message': 'Edit functionality not implemented yet'})
            
#             if Product.objects.filter(pk=pk).exists():
#                 product = Product.objects.get(pk=pk)
                
#                 data = json.loads(request.body.decode('utf-8'))
#                 print(f"Data received for editing: {data}",'oop', request.body.decode('utf-8'))
#                 product_name = data.get('product_name', product.product_name)
#                 product_code = data.get('product_code', product.product_code)
#                 selling_price = data.get('selling_price', product.selling_price)
#                 purchase_price = data.get('purchase_price', product.purchase_price)

#                 product.product_name = product_name
#                 product.product_code = product_code
#                 product.selling_price = selling_price
#                 product.purchase_price = purchase_price
#                 product.save()

#                 return JsonResponse({'message': 'Product updated successfully', 'product': product})
#             else:
#                 return HttpResponse('Product not found', status=404)
#         except Exception as e:
#             return JsonResponse({'message': 'Error updating product', 'error': str(e)}, status=500)
#         pass

#     def product_delete(request, pk):
#         try:
#             if Product.objects.filter(pk=pk).exists():
#                 product = Product.objects.get(pk=pk)
#                 product.delete()
#                 return JsonResponse({'message': 'Product deleted successfully'})
#             else:
#                 return HttpResponse('Product not found', status=404)
#         except Exception as e:
#             return JsonResponse({'message': 'Error deleting product', 'error': str(e)}, status=500)
#         pass