"""
Tests for quiz model functionality.
"""
from django.db.utils import IntegrityError
from quiz.tests.base import QuizTestCase
from quiz.models import Quiz

class QuizModelTests(QuizTestCase):
    """Test quiz model."""

    def test_quiz_calculate_score(self):
        """Test quiz score calculation"""
        # Create an attempt with 3 correct answers out of 5
        attempt = self.create_quiz_attempt(correct_answers=3)
        attempt.complete()
        
        # Verify score calculation
        self.assertEqual(attempt.score, 60.0)  # 3/5 * 100 = 60%
        self.assertTrue(attempt.time_taken > 0)

    def test_quiz_passing_score(self):
        """Test quiz passing score validation"""
        # Test valid passing scores
        valid_scores = [0.0, 50.0, 100.0]
        for score in valid_scores:
            quiz = Quiz.objects.create(
                title=f'Quiz {score}',
                passing_score=score
            )
            self.assertEqual(quiz.passing_score, score)

        # Test invalid passing scores
        invalid_scores = [-1.0, 101.0]
        for score in invalid_scores:
            with self.assertRaises(IntegrityError):
                Quiz.objects.create(
                    title=f'Quiz {score}',
                    passing_score=score
                )

    def test_quiz_str_representation(self):
        """Test string representation of quiz"""
        quiz = Quiz.objects.create(title='Test Quiz')
        self.assertEqual(str(quiz), 'Test Quiz')

    def test_quiz_question_count(self):
        """Test quiz question count property"""
        self.assertEqual(self.quiz.question_count, 5)  # From QuizTestCase setup
