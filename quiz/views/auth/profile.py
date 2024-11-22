"""
Profile and dashboard views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from quiz.models import QuizAttempt, Quiz

@login_required
def profile(request):
    """Display and update user profile and quiz statistics."""
    user = request.user
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
    }
    return render(request, 'quiz/auth/profile.html', context)

@login_required
def dashboard(request):
    """Display user dashboard with quiz statistics."""
    user = request.user
    quiz_attempts = QuizAttempt.objects.filter(user=user).order_by('-date_attempted')
    available_quizzes = Quiz.objects.filter(is_active=True)

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

    context = {
        'user': user,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'pass_rate': round(pass_rate, 1),
        'recent_attempts': recent_attempts,
        'recommended_quizzes': recommended_quizzes,
        'best_categories': best_categories,
        'available_quizzes': available_quizzes,
    }
    return render(request, 'quiz/auth/dashboard.html', context)
