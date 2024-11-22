"""
Redirect views for authentication.
"""
from django.shortcuts import redirect
from django.urls import reverse


def login_redirect(request):
    """Redirect /accounts/login/ to quiz:login."""
    return redirect('quiz:login')


def register_redirect(request):
    """Redirect /accounts/register/ to quiz:register."""
    return redirect('quiz:register')
