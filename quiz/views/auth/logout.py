"""
Logout view.
"""
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import logging
logger = logging.getLogger('quiz.auth')

@login_required
def logout_view(request):
    """Handle user logout."""
    username = request.user.username
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    logger.info(f'User logged out: {username}')
    return redirect('quiz:login')
