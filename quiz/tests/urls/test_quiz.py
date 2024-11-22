"""
Tests for quiz-related URL configuration.
"""
from django.test import TestCase
from django.urls import reverse, resolve
from quiz.views.quiz_views import (
    QuizListView, QuizStartView, QuizSubmitView,
    QuizResultsView, QuizTakeView
)

class QuizUrlTests(TestCase):
    """Test quiz URL routing."""

    def test_quiz_list_url_resolves(self):
        """Test that quiz list URL resolves to the correct view."""
        url = reverse('quiz:quiz_list')
        self.assertEqual(resolve(url).func.view_class, QuizListView)

    def test_quiz_start_url_resolves(self):
        """Test that quiz start URL resolves to the correct view."""
        url = reverse('quiz:quiz_take', args=[1])
        self.assertEqual(resolve(url).func.view_class, QuizTakeView)

    def test_quiz_submit_url_resolves(self):
        """Test that quiz submit URL resolves to the correct view."""
        url = reverse('quiz:quiz_submit', args=[1])
        self.assertEqual(resolve(url).func.view_class, QuizSubmitView)

    def test_quiz_results_url_resolves(self):
        """Test that quiz results URL resolves to the correct view."""
        url = reverse('quiz:quiz_results', args=[1])
        self.assertEqual(resolve(url).func.view_class, QuizResultsView)

    def test_quiz_list_url_name(self):
        """Test quiz list URL name generates correct path."""
        url = reverse('quiz:quiz_list')
        self.assertEqual(url, '/quizzes/')

    def test_quiz_take_url_name(self):
        """Test quiz take URL name generates correct path."""
        url = reverse('quiz:quiz_take', args=[1])
        self.assertEqual(url, '/quiz/1/take/')

    def test_quiz_submit_url_name(self):
        """Test quiz submit URL name generates correct path."""
        url = reverse('quiz:quiz_submit', args=[1])
        self.assertEqual(url, '/quiz/1/submit/')

    def test_quiz_results_url_name(self):
        """Test quiz results URL name generates correct path."""
        url = reverse('quiz:quiz_results', args=[1])
        self.assertEqual(url, '/quiz/1/results/')
