"""
Quiz detail view.
"""
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from .base import QuizViewMixin
from ...models import Quiz
import logging

logger = logging.getLogger(__name__)

class QuizDetailView(QuizViewMixin, DetailView):
    """Display quiz details."""
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'

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
        
        try:
            # Load questions from bank if needed
            if quiz.bank and not quiz.questions.exists():
                quiz.load_questions_from_bank()
            
            # Get quiz questions with caching
            questions = quiz.get_questions()
            context['questions'] = questions
            
        except Exception as e:
            logger.error(f'Error loading quiz questions: {str(e)}')
            context['error'] = 'Unable to load quiz questions'
        
        context.update({
            'question_count': len(questions),
            'time_limit': self.get_time_limit(),
            'passing_score': quiz.passing_score
        })
        return context
