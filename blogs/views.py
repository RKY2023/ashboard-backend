from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.management import call_command
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import os

htmlContent = '''<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <!-- Font Awesome CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            margin: 0;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }
        h1 {
            text-align: center;
            font-size: 2.5rem;
            color: #333;
        }
        .fa-icon {
            margin-right: 10px;
            color: #007bff;
        }
    </style>
</head>
<body>
    <h1>
        
        Welcome to the <i class="fas fa-fire fa-icon"></i>board &end Home Page
    </h1>
</body>
</html>'''


def home(request):
    return HttpResponse(htmlContent)


@csrf_exempt
@require_http_methods(["POST"])
def run_migrations(request):
    """
    Secure endpoint to run migrations on Vercel.
    Protected by a secret token in environment variables.

    Usage: POST to /migrate/ with header:
    X-Migration-Token: <your-secret-token>
    """
    # Get token from request header
    provided_token = request.headers.get('X-Migration-Token')
    expected_token = os.getenv('MIGRATION_SECRET_TOKEN')

    # Security check
    if not expected_token:
        return JsonResponse({
            'error': 'Migration endpoint not configured',
            'message': 'Set MIGRATION_SECRET_TOKEN in environment variables'
        }, status=500)

    if provided_token != expected_token:
        return JsonResponse({
            'error': 'Unauthorized',
            'message': 'Invalid migration token'
        }, status=401)

    try:
        # Run migrations
        call_command('migrate', '--noinput', verbosity=2)

        return JsonResponse({
            'success': True,
            'message': 'Migrations completed successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Migration failed'
        }, status=500)
