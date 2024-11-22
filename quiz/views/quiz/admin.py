"""
Admin views for quiz management.
"""
from typing import Any, Dict
from django.views.generic import UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from ...models import Quiz

class QuizAdminMixin(UserPassesTestMixin):
    """Mixin to ensure only staff can access admin views."""
    
    def test_func(self):
        """Check if user is staff."""
        return self.request.user.is_staff

class QuizEditView(QuizAdminMixin, UpdateView):
    """View for editing a quiz."""
    model = Quiz
    template_name = 'quiz/admin/quiz_edit.html'
    fields = ['title', 'description', 'passing_score', 'is_active']
    
    def get_success_url(self):
        """Return to quiz detail after successful edit."""
        return reverse_lazy('quiz:quiz_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add extra context for template."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context

class QuizCreateView(QuizAdminMixin, CreateView):
    """View for creating a new quiz."""
    model = Quiz
    template_name = 'quiz/admin/quiz_form.html'
    fields = ['title', 'description', 'passing_score', 'is_active']
    
    def get_success_url(self):
        """Return to quiz detail after successful creation."""
        return reverse_lazy('quiz:quiz_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add extra context for template."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context

class QuizDeleteView(QuizAdminMixin, DeleteView):
    """View for deleting a quiz."""
    model = Quiz
    template_name = 'quiz/admin/quiz_delete.html'
    success_url = reverse_lazy('quiz:quiz_list')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add extra context for template."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Delete'
        return context
