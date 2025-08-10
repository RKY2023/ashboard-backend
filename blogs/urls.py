"""
URL configuration for blogs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from blogs.views import home
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('', home),  # Include the region app URLs
    path('api/', include('api.urls')),  # Include the API app URLs
    path('admin/', admin.site.urls),
    path('region/', include('region.urls')),
    path('sate/', include('state.urls')),
    path('country/', include('country.urls')),
    path('pizza/', include('pizza.urls')),
    path('topping/', include('topping.urls')),
    path('userprofile/', include('userprofile.urls')),
    path('product/', include('product.urls')),
    path('order/', include('order.urls')),
    path('vendor/', include('vendor.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
