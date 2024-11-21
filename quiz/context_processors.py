"""
Context processors for quiz app.
"""
from .models import Quiz, QuizAttempt


def quiz_context(request):
    """Add quiz-related context to all templates."""
    context = {
        'app_name': 'Quiz App',
        'site_title': 'Quiz App - Test Your Knowledge',
        'has_active_quiz': False,
    }
    
    if request.user.is_authenticated:
        # Check for active quiz attempts
        active_attempt = QuizAttempt.objects.filter(
            user=request.user,
            completed_at__isnull=True
        ).first()
        
        if active_attempt:
            context['has_active_quiz'] = True
            context['active_quiz'] = active_attempt.quiz
    
    return context
