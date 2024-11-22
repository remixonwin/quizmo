"""
Base test class for quiz submission tests.
"""
from quiz.tests.base import QuizTestBase
from quiz.models import QuizAttempt, Quiz
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

class QuizSubmissionTestBase(QuizTestBase):
    """Base test class for quiz submission tests."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
        self.csrf_token = self.client.cookies.get('csrftoken', None)
        if not self.csrf_token:
            self.csrf_token = self.client.cookies['csrftoken'] = 'test-csrf-token'

    def create_quiz_attempt(self):
        """Create a quiz attempt."""
        return QuizAttempt.objects.create(
            user=self.test_user,
            quiz=self.quiz,
            started_at=self.now
        )

    def get_submission_url(self, attempt):
        """Get the submission URL."""
        return reverse('quiz:submit_quiz', args=[self.quiz.id, attempt.id])

    def prepare_submission_data(self, answers=None, metadata=None):
        """Prepare submission data."""
        if answers is None:
            answers = []
            for question in self.questions:
                if question.is_active:
                    answers.append({
                        'question_id': question.id,
                        'selected_choices': [choice.id for choice in question.choices.filter(is_correct=True)]
                    })

        if metadata is None:
            metadata = {
                'time_taken': 600,  # 10 minutes
                'browser_info': {
                    'browser': 'Chrome',
                    'version': '91.0.4472.124',
                    'platform': 'Windows'
                }
            }

        return {
            'answers': answers,
            'metadata': metadata
        }

    def submit_quiz(self, attempt, data, content_type='application/json'):
        """Submit a quiz attempt."""
        url = self.get_submission_url(attempt)
        headers = {
            'X-CSRFToken': self.csrf_token,
            'Content-Type': content_type
        }
        return self.client.post(
            url,
            data=json.dumps(data) if content_type == 'application/json' else data,
            content_type=content_type,
            **headers
        )
