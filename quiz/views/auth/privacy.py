"""
Privacy policy view.
"""
from django.shortcuts import render


def privacy_policy(request):
    """Display privacy policy page."""
    return render(request, 'quiz/auth/privacy_policy.html')
