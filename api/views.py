from rest_framework.response import Response
from rest_framework.decorators import api_view

# @api_view(['GET'])
# def api_home(request):
#     return Response({"message": "Welcome to the Region API Home Page"})

# def api_home(request):
#     # return HttpResponse("Welcome to the Region API Home Page")
#     return HttpResponse({"message": "Welcome to the Region API Home Page"})


from django.views import View
from django.http import JsonResponse
from region.models import Region

class ApiHomeView(View):
    def get(self, request):
        Regions = Region.objects.all()
        data = list(Regions.values())
        print('tt', type (Regions), type (data), Regions, data)
        return JsonResponse({"message": "Welcome to the Region API Home Page", 'data': data, 'queryset': repr(Regions)})
    def post(self, request):
        region_name = request.POST.get('region_name')
        region_code = request.POST.get('region_code')
        region_slug = request.POST.get('region_slug')
        region_description = request.POST.get('region_description')

        region_data = Region(region_name=region_name, region_code=region_code, 
                             region_slug=region_slug, region_description=region_description)
        region_data.save()
        return JsonResponse({"message": "success", "data": {"id": region_data.id, "region_name": region_data.region_name}})
    def put(self, request):
        region_id = request.POST.get('id')
        Region.objects.filter(id=region_id).update(
            region_name=request.POST.get('region_name'),
            region_code=request.POST.get('region_code'),
            region_slug=request.POST.get('region_slug'),
            region_description=request.POST.get('region_description')
        )
        return JsonResponse({"message": "region updated successfully"})
    def delete(self, request):
        region_id = request.POST.get('id')
        Region.objects.filter(id=region_id).delete()
        return JsonResponse({"message": "Region deleted successfully"})
