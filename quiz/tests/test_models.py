"""
Tests for quiz models.
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from quiz.tests.base import QuizTestCase
from quiz.models import Quiz, Question, Choice, QuizAttempt

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

class QuestionModelTests(QuizTestCase):
    """Test question model."""

    def test_question_order(self):
        """Test question ordering"""
        # Questions are already created in setUpTestData
        # Verify they are in correct order
        questions = Question.objects.filter(quiz=self.quiz).order_by('order')
        for i, question in enumerate(questions):
            self.assertEqual(question.order, i)

    def test_question_points(self):
        """Test question points validation"""
        # Test valid points
        valid_points = [1, 5, 10]
        for points in valid_points:
            question = Question.objects.create(
                quiz=self.quiz,
                text=f'Question worth {points} points',
                points=points,
                order=len(self.questions) + 1
            )
            self.assertEqual(question.points, points)

        # Test invalid points
        invalid_points = [-1, 0]
        for points in invalid_points:
            with self.assertRaises(IntegrityError):
                Question.objects.create(
                    quiz=self.quiz,
                    text=f'Question worth {points} points',
                    points=points,
                    order=len(self.questions) + 1
                )

class ChoiceModelTests(QuizTestCase):
    """Test choice model."""

    def test_choice_without_question(self):
        """Test choice creation without question"""
        with self.assertRaises(IntegrityError):
            Choice.objects.create(
                text="Invalid Choice",
                is_correct=True,
                order=0
            )

    def test_choice_order(self):
        """Test choice ordering"""
        # Get first question's choices
        question = self.questions[0]
        choices = Choice.objects.filter(question=question).order_by('order')
        
        # Verify order
        for i, choice in enumerate(choices):
            self.assertEqual(choice.order, i)

    def test_multiple_correct_choices(self):
        """Test multiple correct choices validation"""
        question = self.questions[0]
        
        # Try to create another correct choice
        with self.assertRaises(IntegrityError):
            Choice.objects.create(
                question=question,
                text="Another Correct Answer",
                is_correct=True,
                order=4
            )

class QuizAttemptModelTests(QuizTestCase):
    """Test quiz attempt model."""

    def test_attempt_score_calculation(self):
        """Test attempt score calculation"""
        # Create attempt with all correct answers
        attempt = self.create_quiz_attempt(correct_answers=5)
        attempt.complete()
        
        self.assertEqual(attempt.score, 100.0)
        self.assertIsNotNone(attempt.completed_at)
        self.assertTrue(attempt.time_taken > 0)

    def test_attempt_partial_score(self):
        """Test partial score calculation"""
        # Create attempt with some correct answers
        attempt = self.create_quiz_attempt(correct_answers=3)
        attempt.complete()
        
        self.assertEqual(attempt.score, 60.0)  # 3/5 * 100
        self.assertIsNotNone(attempt.completed_at)
        self.assertTrue(attempt.time_taken > 0)

    def test_attempt_no_answers(self):
        """Test attempt with no answers"""
        attempt = self.create_quiz_attempt(correct_answers=0)
        attempt.complete()
        
        self.assertEqual(attempt.score, 0.0)
        self.assertIsNotNone(attempt.completed_at)
        self.assertTrue(attempt.time_taken > 0)
