from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from region.models import Region

# Create your views here.
class RegionView(View):
    def get(self, request):
        regions = Region.objects.all()
        return JsonResponse({'messagde': "success", 'data': list(regions.values())})

    def post(self, request):
        region_name = request.POST.get('region_name')
        region_code = request.POST.get('region_code')
        region_slug = request.POST.get('region_slug')
        region_description = request.POST.get('region_description')

        region_data = Region(region_name=region_name, region_code=region_code, 
                             region_slug=region_slug, region_description=region_description)
        region_data.save()
        return HttpResponse({'message': "success", 'data': region_data})
def region_list_create(request):
    try:
        if request.method == 'POST':
            region_name = request.POST.get('region_name')
            region_code = request.POST.get('region_code')
            region_data = Region(region_name=region_name, region_code=region_code)
            region_data.save()
        else:
            return HttpResponse({'message': "fail", 'error': 'Invalid request method'})
    except Exception as e:
        return HttpResponse({'message': "fail", 'error': str(e)})
    finally:
        return HttpResponse({'message': "server error", 'error': 'Server error occurred'})

def test(request):
    return HttpResponse({'message': "success", 'data': 'test'})