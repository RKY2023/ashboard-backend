from django.shortcuts import render, get_list_or_404, get_object_or_404
# from django.views import View
from .models import Vendor
# from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VendorSerializer
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend


class VendorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'vendor_name': ['icontains'],
        'email': ['icontains'],
        'phone_no': ['icontains'],
        'address': ['icontains'],
    }

class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    
    # def retrieve(self, request, pk=None):
    #     vendor = get_object_or_404(Vendor, pk=pk)
    #     serialize = self.get_serializer(vendor)
    #     return Response({'message': 'success', 'vendor': serialize.data})
    
    # def update(self, request, pk=None):
    #     vendor = get_object_or_404(Vendor, pk=pk)
    #     serialize = self.get_serializer(vendor, data=request.data, partial=True)
    #     serialize.is_valid(raise_exception=True)
    #     serialize.save()
    #     return Response({'message': 'success', 'vendor': serialize.data})
    
    # def destroy(self, request, pk=None):
    #     vendor = get_object_or_404(Vendor, pk=pk)
    #     vendor.delete()
    #     return Response({'message': 'Vendor deleted successfully'})
    
    
    # def retrieve(self, request, pk=None):
        
        
        

# class VendorView(APIView):
#     def get(self, request, pk=None):
#         if pk:
#             try:
#                 vendor = Vendor.objects.get(pk=pk)
#                 serialize = VendorSerializer(vendor)
#                 return Response({'message': 'success', 'vendor': serialize.data}, status=status.HTTP_200_OK)
#             except Vendor.DoesNotExist:
#                 return Response({'message': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             vendors = Vendor.objects.all()
#             serialize = VendorSerializer(vendors, many=True)
#             return Response({'message': 'success', 'vendors': serialize.data}, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = VendorSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Vendor created successfully', 'vendor': serializer.data}, status=status.HTTP_201_CREATED)
#         return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk=None):
#         if not pk:
#             return Response({'message': 'Vendor ID is required for update'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             vendor = Vendor.objects.get(pk=pk)
#             serializer = VendorSerializer(vendor, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'message': 'Vendor updated successfully', 'vendor': serializer.data}, status=status.HTTP_200_OK)
#             return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Vendor.DoesNotExist:
#             return Response({'message': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
#         pass

#     def delete(self, request, pk=None):
#         if not pk:
#             return Response({'message': 'Vendor ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             vendor = Vendor.objects.get(pk=pk)
#             vendor.delete()
#             return Response({'message': 'Vendor deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
#         except Vendor.DoesNotExist:
#             return Response({'message': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
#         pass

# Create your views here.
# class VendorView(View):
#     def vendor_list(request):
#         vendors = Vendor.objects.all()
#         vendors_data = list(vendors.values())
#         return JsonResponse({'message': 'success', 'vendors': vendors_data})
#         pass

#     def vendor_detail(request, pk):
#         try:
#             if Vendor.objects.filter(pk=pk).exists():
#                 vendor = Vendor.objects.get(pk=pk)
#                 vendor_data = dict(vendor)
#                 return JsonResponse({'message': 'success', 'vendor': vendor_data})
#             else:
#                 return HttpResponse('Vendor not found', status=404)
#         except Exception as e:
#             return JsonResponse({'message': 'Error fetching vendor', 'error': str(e)}, status=500)
#         pass

#     def vendor_add(request):
#         try:
#             vendor_name = request.POST.get('vendor_name')
#             phone_no = request.POST.get('phone_no')
#             address = request.POST.get('address')
#             email = request.POST.get('email')
#             if vendor_name:
#                 vendor = Vendor.objects.create(
#                     vendor_name=vendor_name,
#                     phone_no=phone_no,
#                     address=address,
#                     email=email
#                 )
#                 return JsonResponse({'message': 'Vendor added successfully', 'vendor': str(vendor)})
#             else:
#                 return JsonResponse({'message': 'Invalid data'}, status=400)
#         except Exception as e:
#             return JsonResponse({'message': 'Error adding vendor', 'error': str(e)}, status=500)
#         pass

#     def vendor_edit(request, pk):
#         try:
#             if Vendor.objects.filter(pk=pk).exists():
#                 vendor = Vendor.objects.get(pk=pk)
#                 vendor_name = request.POST.get('vendor_name', vendor.vendor_name)
#                 phone_no = request.POST.get('phone_no', vendor.phone_no)
#                 address = request.POST.get('address', vendor.address)
#                 email = request.POST.get('email', vendor.email)

#                 vendor.vendor_name = vendor_name
#                 vendor.phone_no = phone_no
#                 vendor.address = address
#                 vendor.email = email
#                 vendor.save()

#                 return JsonResponse({'message': 'Vendor updated successfully', 'vendor': str(vendor)})
#             else:
#                 return HttpResponse('Vendor not found', status=404)
#         except Exception as e:
#             return JsonResponse({'message': 'Error updating vendor', 'error': str(e)}, status=500)
#         pass

#     def vendor_delete(request, pk):
#         try:
#             if Vendor.objects.filter(pk=pk).exists():
#                 vendor = Vendor.objects.get(pk=pk)
#                 vendor.delete()
#                 return JsonResponse({'message': 'Vendor deleted successfully'})
#             else:
#                 return HttpResponse('Vendor not found', status=404)
#         except Exception as e:
#             return JsonResponse({'message': 'Error deleting vendor', 'error': str(e)}, status=500)
#         pass