"""
Base test class for quiz tests.
"""
from django.test import TestCase
from django.utils import timezone
from quiz.models import Quiz, QuizAttempt
from .auth import AuthTestCase

class QuizTestCase(AuthTestCase):
    """Base test case for quiz tests."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test quiz data."""
        super().setUpTestData()
        
        # Create test quiz
        cls.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            created_by=cls.test_admin,
            pass_mark=80.0,
            time_limit=30,
            answers_at_end=True,
            is_active=True
        )
        
        # Create additional quizzes for testing
        cls.inactive_quiz = Quiz.objects.create(
            title='Inactive Quiz',
            description='Inactive Quiz Description',
            created_by=cls.test_admin,
            is_active=False
        )
        
        cls.timed_quiz = Quiz.objects.create(
            title='Timed Quiz',
            description='Timed Quiz Description',
            created_by=cls.test_admin,
            time_limit=10,
            is_active=True
        )
    
    def create_quiz_attempt(self, quiz=None, user=None, answers=None):
        """Create a quiz attempt.
        
        Args:
            quiz: Quiz to attempt. Defaults to self.quiz
            user: User making the attempt. Defaults to self.test_user
            answers: List of (question, choice) tuples for answers
        """
        quiz = quiz or self.quiz
        user = user or self.test_user
        
        attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            started_at=timezone.now()
        )
        
        if answers:
            for question, choice in answers:
                attempt.answers.create(
                    question=question,
                    choice=choice
                )
        
        return attempt
