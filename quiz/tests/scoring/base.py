"""
Base test class for quiz scoring tests.
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from quiz.models import Quiz, Question, Choice, QuizAttempt

class BaseScoringTest(TestCase):
    """Base class for scoring tests with common setup and utility methods."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test quiz description',
            pass_mark=70.0,
            created_by=self.user
        )
        
        # Create questions with different difficulties and points
        self.questions = []
        
        # Easy question (1 point)
        q1 = Question.objects.create(
            quiz=self.quiz,
            text='Question 1',
            difficulty='easy',
            points=1.0,
            order=1
        )
        Choice.objects.create(question=q1, text='Correct', is_correct=True, order=1)
        Choice.objects.create(question=q1, text='Wrong', is_correct=False, order=2)
        self.questions.append(q1)
        
        # Medium question (2 points)
        q2 = Question.objects.create(
            quiz=self.quiz,
            text='Question 2',
            difficulty='medium',
            points=2.0,
            order=2
        )
        Choice.objects.create(question=q2, text='Correct', is_correct=True, order=1)
        Choice.objects.create(question=q2, text='Wrong', is_correct=False, order=2)
        self.questions.append(q2)
        
        # Hard question (3 points)
        q3 = Question.objects.create(
            quiz=self.quiz,
            text='Question 3',
            difficulty='hard',
            points=3.0,
            order=3
        )
        Choice.objects.create(question=q3, text='Correct', is_correct=True, order=1)
        Choice.objects.create(question=q3, text='Wrong', is_correct=False, order=2)
        self.questions.append(q3)
        
        # Create active attempt
        self.attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            started_at=timezone.now(),
            metadata={
                'total_points': 0.0,
                'earned_points': 0.0,
                'correct_answers': 0,
                'total_questions': 0,
                'difficulty_stats': {
                    'easy': {'total': 0, 'correct': 0},
                    'medium': {'total': 0, 'correct': 0},
                    'hard': {'total': 0, 'correct': 0}
                },
                'completion_time': 0.0
            }
        )
        
        # Cache the attempt
        cache_key = f'attempt_{self.user.id}_{self.quiz.id}'
        cache.set(cache_key, self.attempt, timeout=300)
