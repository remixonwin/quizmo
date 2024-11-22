"""
Profile and dashboard views.
"""
from typing import Dict, Any
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from quiz.models import QuizAttempt, Quiz
import logging

logger = logging.getLogger(__name__)

@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """Display and update user profile and quiz statistics."""
    user = request.user
    logger.info(f"Loading profile for user {user.username}")
    
    if not user.is_active:
        logger.warning(f"Inactive user {user.username} attempted to access profile")
        raise PermissionDenied("Your account is not active. Please verify your email.")
    
    try:
        quiz_attempts = QuizAttempt.objects.filter(user=user).order_by('-date_attempted')
        total_attempts = quiz_attempts.count()
        passed_attempts = quiz_attempts.filter(passed=True).count()
        pass_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0

        context = {
            'user': user,
            'quiz_attempts': quiz_attempts[:10],  # Show last 10 attempts
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'pass_rate': round(pass_rate, 1),
            'last_login': user.last_login,
            'date_joined': user.date_joined,
        }
        logger.info(f"Profile loaded successfully for user {user.username}")
        return render(request, 'quiz/auth/profile.html', context)
    except Exception as e:
        logger.error(f"Error loading profile for user {user.username}: {str(e)}")
        raise

@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Display user dashboard with quiz statistics."""
    user = request.user
    logger.info(f"Loading dashboard for user {user.username}")
    
    if not user.is_active:
        logger.warning(f"Inactive user {user.username} attempted to access dashboard")
        messages.warning(request, "Your account is not active. Please verify your email.")
        return HttpResponseForbidden("Your account is not active. Please verify your email.")
    
    try:
        # Get quiz attempts with select_related for better performance
        quiz_attempts = QuizAttempt.objects.filter(user=user).select_related('quiz').order_by('-date_attempted')
        available_quizzes = Quiz.objects.filter(is_active=True).select_related()

        # Calculate statistics
        total_attempts = quiz_attempts.count()
        passed_attempts = quiz_attempts.filter(passed=True).count()
        pass_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Get recent activity
        recent_attempts = quiz_attempts[:5]  # Last 5 attempts
        
        # Get recommended quizzes (quizzes user hasn't attempted yet)
        attempted_quiz_ids = quiz_attempts.values_list('quiz_id', flat=True)
        recommended_quizzes = available_quizzes.exclude(id__in=attempted_quiz_ids)[:3]
        
        # Get best performing categories
        category_stats = {}
        for attempt in quiz_attempts:
            category = attempt.quiz.category
            if category not in category_stats:
                category_stats[category] = {'attempts': 0, 'passed': 0}
            category_stats[category]['attempts'] += 1
            if attempt.passed:
                category_stats[category]['passed'] += 1
        
        best_categories = sorted(
            category_stats.items(),
            key=lambda x: (x[1]['passed'] / x[1]['attempts'] if x[1]['attempts'] > 0 else 0),
            reverse=True
        )[:3]
        
        # Get progress over time
        monthly_stats = quiz_attempts.extra(
            select={'month': "DATE_TRUNC('month', date_attempted)"}
        ).values('month').annotate(
            total=Count('id'),
            passed=Count('id', filter=Q(passed=True)),
            avg_score=Avg('score')
        ).order_by('-month')[:6]

        context = {
            'user': user,
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'pass_rate': round(pass_rate, 1),
            'recent_attempts': recent_attempts,
            'recommended_quizzes': recommended_quizzes,
            'best_categories': best_categories,
            'available_quizzes': available_quizzes,
            'monthly_stats': monthly_stats,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
        }
        logger.info(f"Dashboard loaded successfully for user {user.username}")
        return render(request, 'quiz/auth/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error loading dashboard for user {user.username}: {str(e)}")
        raise
