from drf_spectacular.views import SpectacularSwaggerView


class DarkSwaggerView(SpectacularSwaggerView):
    template_name = 'swagger_dark.html'
