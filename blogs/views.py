from django.http import HttpResponse
from django.shortcuts import render

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
