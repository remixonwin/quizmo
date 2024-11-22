"""
Concurrency and security tests for quiz submission.
"""
from .base import QuizSubmissionTestBase
from django.urls import reverse
from quiz.models import QuizAttempt
from django.utils import timezone
from django.contrib.auth.models import User

class QuizSubmissionConcurrencySecurityTests(QuizSubmissionTestBase):
    """Test concurrency and security aspects of quiz submission."""

    def test_concurrent_submissions(self):
        """Test handling of concurrent submissions for the same quiz."""
        # Create initial quiz attempt
        first_attempt = self.create_quiz_attempt()
        
        # Create a second attempt before completing the first
        second_attempt = self.create_quiz_attempt()
        
        # Try to submit both attempts
        data = self.prepare_submission_data()
        
        # Submit first attempt
        first_response = self.submit_quiz(first_attempt, data)
        self.assertEqual(first_response.status_code, 200)
        
        # Try to submit second attempt
        second_response = self.submit_quiz(second_attempt, data)
        self.assertEqual(second_response.status_code, 400)
        self.assertIn('error', second_response.json())
        self.assertIn('active attempt', second_response.json()['error'].lower())

    def test_unauthorized_submission(self):
        """Test submission from unauthorized user."""
        attempt = self.create_quiz_attempt()
        
        # Create and login as different user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.force_login(other_user)
        
        data = self.prepare_submission_data()
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json())
        self.assertIn('unauthorized', response.json()['error'].lower())

    def test_csrf_protection(self):
        """Test CSRF protection for quiz submission."""
        attempt = self.create_quiz_attempt()
        data = self.prepare_submission_data()
        
        # Try to submit without CSRF token
        response = self.client.post(
            self.get_submission_url(attempt),
            data=data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)

    def test_invalid_attempt_id(self):
        """Test submission with invalid attempt ID."""
        attempt = self.create_quiz_attempt()
        invalid_id = attempt.id + 1000  # Ensure it doesn't exist
        
        data = self.prepare_submission_data()
        url = reverse('quiz:submit_quiz', args=[self.quiz.id, invalid_id])
        
        response = self.client.post(
            url,
            data=data,
            content_type='application/json',
            HTTP_X_CSRFTOKEN=self.csrf_token
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
        self.assertIn('not found', response.json()['error'].lower())

    def test_rate_limiting(self):
        """Test rate limiting for quiz submissions."""
        attempt = self.create_quiz_attempt()
        data = self.prepare_submission_data()
        
        # Submit multiple times in quick succession
        for _ in range(10):
            response = self.submit_quiz(attempt, data)
            if response.status_code == 429:  # Too Many Requests
                break
        else:
            self.fail("Rate limiting not enforced")
