from rest_framework.authentication import SessionAuthentication
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication without CSRF checks for API endpoints
    """
    def enforce_csrf(self, request):
        return  # Skip CSRF check


class CsrfExemptSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'blogs.authentication.CsrfExemptSessionAuthentication'
    name = 'sessionAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid'
        }
