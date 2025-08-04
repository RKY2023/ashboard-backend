from django.urls import path, include
from . import views
# from rest_framework.routers import DefaultRouter
from region.views import region_list_create, test

# router = DefaultRouter()
# router.register(r'region', views.RegionView, basename='region')


urlpatterns = [
    # path('', include(router.urls)),
    path('', views.RegionView.as_view(), name='region-list'),
    # path('', region_list_create, name='region-list-create'),
    path('test/', test, name='test'),
    # path('/test', views.test),
    # path('region/create', views.region_list_create),
]