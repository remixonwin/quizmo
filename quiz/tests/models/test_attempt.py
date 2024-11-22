"""
Tests for quiz attempt model functionality.
"""
from quiz.tests.base import QuizTestCase
from quiz.models import QuizAttempt

class QuizAttemptModelTests(QuizTestCase):
    """Test quiz attempt model."""

    def test_attempt_score_calculation(self):
        """Test attempt score calculation"""
        # Create an attempt with all correct answers
        attempt = self.create_quiz_attempt(correct_answers=5)
        attempt.complete()
        
        self.assertEqual(attempt.score, 100.0)
        self.assertTrue(attempt.is_passing)

    def test_attempt_partial_score(self):
        """Test partial score calculation"""
        # Create an attempt with some correct answers
        attempt = self.create_quiz_attempt(correct_answers=3)
        attempt.complete()
        
        self.assertEqual(attempt.score, 60.0)  # 3/5 * 100
        self.assertTrue(attempt.is_passing)  # Default passing score is 60%

    def test_attempt_no_answers(self):
        """Test attempt with no answers"""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user
        )
        attempt.complete()
        
        self.assertEqual(attempt.score, 0.0)
        self.assertFalse(attempt.is_passing)

    def test_attempt_str_representation(self):
        """Test string representation of attempt"""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user
        )
        expected = f'{self.user.username} - {self.quiz.title} Attempt'
        self.assertEqual(str(attempt), expected)
