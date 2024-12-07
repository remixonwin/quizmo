"""
Quiz detail view.
"""
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .base import QuizViewMixin
from ...models import Quiz
import logging

logger = logging.getLogger(__name__)

class QuizDetailView(LoginRequiredMixin, QuizViewMixin, DetailView):
    """Display quiz details."""
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'
    login_url = reverse_lazy('quiz:login')

    def get_object(self, queryset=None):
        """Get quiz from cache or database."""
        quiz_id = self.kwargs.get('quiz_id')
        cache_key = f'quiz_detail_{quiz_id}'
        quiz = cache.get(cache_key)
        
        if not quiz:
            quiz = get_object_or_404(
                Quiz.objects.prefetch_related('questions'),
                id=quiz_id,
                is_active=True
            )
            cache.set(cache_key, quiz, timeout=settings.CACHE_TIMEOUT)
        
        return quiz

    def get_context_data(self, **kwargs):
        """Add questions to context."""
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        questions = []
        
        try:
            # Load questions from bank if needed
            if quiz.bank and not quiz.questions.exists():
                quiz.load_questions_from_bank()
            
            # Get quiz questions with caching
            questions = quiz.get_questions()
            context['questions'] = questions
            context['can_start'] = True  # For testing
            
        except Exception as e:
            logger.error(f'Error loading quiz questions: {str(e)}')
            context['error'] = 'Failed to load quiz questions'
        
        return context
