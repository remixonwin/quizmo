"""
Basic quiz submission tests.
"""
from .base import QuizSubmissionTestBase
from django.urls import reverse
from quiz.models import QuizAttempt
from django.utils import timezone

class BasicQuizSubmissionTests(QuizSubmissionTestBase):
    """Test basic quiz submission functionality."""

    def test_quiz_submission_perfect_score(self):
        """Test quiz submission with all correct answers."""
        attempt = self.create_quiz_attempt()
        data = self.prepare_submission_data()
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['score'], 100)
        self.assertTrue(response.json()['passed'])
        
        # Verify attempt is completed
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)
        self.assertEqual(attempt.score, 100)
        self.assertTrue(attempt.passed)

    def test_quiz_submission_partial_score(self):
        """Test quiz submission with mix of correct and wrong answers."""
        attempt = self.create_quiz_attempt()
        
        # Prepare submission with some wrong answers
        answers = []
        for question in self.questions:
            if question.is_active:
                # Get a mix of correct and incorrect choices
                choices = list(question.choices.all())
                selected_choices = [choices[0].id]  # Just select first choice
                answers.append({
                    'question_id': question.id,
                    'selected_choices': selected_choices
                })
        
        data = self.prepare_submission_data(answers=answers)
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response.json()['score'], 100)
        
        # Verify attempt is completed
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)
        self.assertLess(attempt.score, 100)

    def test_quiz_submission_validation(self):
        """Test validation of quiz submissions."""
        attempt = self.create_quiz_attempt()
        
        # Prepare submission data with missing answer
        answers = []
        # Skip first question
        for question in self.questions[1:]:
            if question.is_active:
                answers.append({
                    'question_id': question.id,
                    'selected_choices': [choice.id for choice in question.choices.filter(is_correct=True)]
                })
        
        data = self.prepare_submission_data(answers=answers)
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
        # Verify attempt is not completed
        attempt.refresh_from_db()
        self.assertIsNone(attempt.completed_at)
        self.assertIsNone(attempt.score)

    def test_quiz_submission_time_limit(self):
        """Test submission after time limit has expired."""
        # Create a quiz attempt with start time 31 minutes ago
        attempt = QuizAttempt.objects.create(
            user=self.test_user,
            quiz=self.quiz,
            started_at=timezone.now() - timezone.timedelta(minutes=31)
        )
        
        data = self.prepare_submission_data()
        response = self.submit_quiz(attempt, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('time limit', response.json()['error'].lower())
