"""
Tests for quiz scoring validation.
"""
import json
from django.urls import reverse
from django.utils import timezone
from quiz.tests.scoring.base import BaseScoringTest

class ValidationTests(BaseScoringTest):
    """Test validation of quiz submissions."""

    def test_invalid_submission(self):
        """Test submission with invalid data"""
        # Submit with missing question
        answers = [
            {
                'question_id': self.questions[0].id,
                'choice_id': self.questions[0].choices.first().id
            }
        ]
        
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json'
        )
        
        # Check bad request response
        self.assertEqual(response.status_code, 400)
        
        # Verify attempt not completed
        attempt = self.attempt.__class__.objects.get(id=self.attempt.id)
        self.assertIsNone(attempt.completed_at)
        self.assertIsNone(attempt.score)

    def test_invalid_question_id(self):
        """Test submission with non-existent question ID"""
        answers = [
            {
                'question_id': 9999,  # Non-existent question
                'choice_id': self.questions[0].choices.first().id
            }
        ]
        
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid question ID', response.json()['error'])

    def test_invalid_choice_id(self):
        """Test submission with non-existent choice ID"""
        answers = [
            {
                'question_id': self.questions[0].id,
                'choice_id': 9999  # Non-existent choice
            }
        ]
        
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid choice ID', response.json()['error'])

    def test_missing_metadata(self):
        """Test submission without required metadata"""
        answers = [
            {
                'question_id': self.questions[0].id,
                'choice_id': self.questions[0].choices.first().id
            }
        ]
        
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),  # Missing metadata
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing metadata', response.json()['error'])
