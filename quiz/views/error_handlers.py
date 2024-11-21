"""
Error handler views for the quiz app.
"""
from django.shortcuts import render

def handler403(request, exception=None):
    """Handle 403 Forbidden errors."""
    return render(request, 'quiz/errors/403.html', status=403)

def handler404(request, exception=None):
    """Handle 404 Not Found errors."""
    return render(request, 'quiz/errors/404.html', status=404)

def handler500(request):
    """Handle 500 Internal Server Error."""
    return render(request, 'quiz/errors/500.html', status=500)
