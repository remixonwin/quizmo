"""
Tests for basic quiz views.
"""
from django.urls import reverse
from quiz.models import QuizAttempt
from quiz.tests.views.base import BaseViewTest

class QuizViewTests(BaseViewTest):
    """Test basic quiz views."""

    def test_quiz_list_view(self):
        """Test the quiz list view"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_list.html')
        self.assertIn(self.quiz, response.context['quizzes'])

    def test_quiz_detail_view(self):
        """Test the quiz detail view"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.get(
            reverse('quiz:quiz_detail', kwargs={'pk': self.quiz.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_detail.html')
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(len(response.context['questions']), 5)

    def test_quiz_start_view(self):
        """Test starting a quiz"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.post(
            reverse('quiz:quiz_start', kwargs={'pk': self.quiz.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirects to quiz attempt
        
        self.assertTrue(
            QuizAttempt.objects.filter(
                quiz=self.quiz,
                user=self.test_user
            ).exists()
        )

    def test_quiz_attempt_view(self):
        """Test quiz attempt view"""
        self.client.login(username=self.test_user.username, password='testpass123')
        attempt = self.create_quiz_attempt()
        
        response = self.client.get(
            reverse('quiz:quiz_attempt', kwargs={'pk': attempt.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_attempt.html')
        self.assertEqual(response.context['attempt'], attempt)
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(len(response.context['questions']), 5)
