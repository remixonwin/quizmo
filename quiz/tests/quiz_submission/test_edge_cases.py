"""
Edge case tests for quiz submission.
"""
from .base import QuizSubmissionTestBase
from django.urls import reverse
from quiz.models import QuizAttempt
from django.utils import timezone

class QuizSubmissionEdgeCaseTests(QuizSubmissionTestBase):
    """Test edge cases in quiz submission."""

    def test_inactive_questions(self):
        """Test submission with inactive questions."""
        attempt = self.create_quiz_attempt()
        
        # Make all questions inactive
        for question in self.questions:
            question.is_active = False
            question.save()
        
        data = self.prepare_submission_data()
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('no active questions', response.json()['error'].lower())

    def test_invalid_json_data(self):
        """Test submission with invalid JSON data."""
        attempt = self.create_quiz_attempt()
        
        # Submit with invalid JSON
        response = self.client.post(
            self.get_submission_url(attempt),
            data='invalid json',
            content_type='application/json',
            HTTP_X_CSRFTOKEN=self.csrf_token
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('invalid json', response.json()['error'].lower())

    def test_malformed_metadata(self):
        """Test submission with malformed metadata."""
        attempt = self.create_quiz_attempt()
        
        # Prepare submission with malformed metadata
        data = self.prepare_submission_data()
        data['metadata'] = 'invalid'
        
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('metadata', response.json()['error'].lower())

    def test_invalid_choice_combinations(self):
        """Test submission with invalid choice combinations."""
        attempt = self.create_quiz_attempt()
        
        # Prepare submission with choices from wrong questions
        answers = []
        wrong_choices = []
        for question in self.questions:
            if question.is_active:
                wrong_choices.extend([choice.id for choice in question.choices.all()])
        
        # Use choices from first question for all questions
        for question in self.questions:
            if question.is_active:
                answers.append({
                    'question_id': question.id,
                    'selected_choices': wrong_choices[:2]  # Use first two choices for all questions
                })
        
        data = self.prepare_submission_data(answers=answers)
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('invalid choice', response.json()['error'].lower())

    def test_duplicate_answers(self):
        """Test submission with duplicate answers for the same question."""
        attempt = self.create_quiz_attempt()
        
        # Prepare submission with duplicate answers
        answers = []
        first_question = next(q for q in self.questions if q.is_active)
        answers.append({
            'question_id': first_question.id,
            'selected_choices': [choice.id for choice in first_question.choices.filter(is_correct=True)]
        })
        # Add duplicate answer for first question
        answers.append({
            'question_id': first_question.id,
            'selected_choices': [choice.id for choice in first_question.choices.all()]
        })
        
        data = self.prepare_submission_data(answers=answers)
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('duplicate', response.json()['error'].lower())

    def test_missing_metadata(self):
        """Test submission without metadata."""
        attempt = self.create_quiz_attempt()
        
        # Prepare submission without metadata
        data = self.prepare_submission_data()
        del data['metadata']
        
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('metadata', response.json()['error'].lower())
