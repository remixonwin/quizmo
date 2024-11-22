"""
Tests for quiz progress tracking.
"""
from django.urls import reverse
from quiz.tests.views.base import BaseViewTest

class QuizProgressTests(BaseViewTest):
    """Test quiz progress tracking."""

    def test_quiz_progress(self):
        """Test tracking quiz progress"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        # Create multiple attempts with different scores
        attempts = []
        scores = [100.0, 60.0, 80.0]
        for score in scores:
            correct = int((score / 100.0) * 5)  # 5 questions total
            attempt = self.create_quiz_attempt(correct_answers=correct)
            attempt.complete()
            attempts.append(attempt)
        
        # Check progress view
        response = self.client.get(reverse('quiz:quiz_progress'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_progress.html')
        
        # Verify progress data
        progress = response.context['progress']
        self.assertEqual(len(progress['attempts']), 3)
        self.assertEqual(progress['average_score'], 80.0)
        self.assertEqual(progress['best_score'], 100.0)
        self.assertEqual(progress['total_attempts'], 3)
