import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from ..models import Quiz, Question, Choice, QuizAttempt, UserAnswer

class QuizScoringTest(TestCase):
    def setUp(self):
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
            pass_mark=70.0
        )
        
        # Create questions with different difficulties and points
        self.questions = []
        
        # Easy question (1 point)
        q1 = Question.objects.create(
            quiz=self.quiz,
            text='Easy question',
            difficulty='easy',
            points=Decimal('1.00'),
            order=1
        )
        Choice.objects.create(question=q1, text='Correct', is_correct=True, order=1)
        Choice.objects.create(question=q1, text='Wrong', is_correct=False, order=2)
        self.questions.append(q1)
        
        # Medium question (2 points)
        q2 = Question.objects.create(
            quiz=self.quiz,
            text='Medium question',
            difficulty='medium',
            points=Decimal('2.00'),
            order=2
        )
        Choice.objects.create(question=q2, text='Correct', is_correct=True, order=1)
        Choice.objects.create(question=q2, text='Wrong', is_correct=False, order=2)
        self.questions.append(q2)
        
        # Hard question (3 points)
        q3 = Question.objects.create(
            quiz=self.quiz,
            text='Hard question',
            difficulty='hard',
            points=Decimal('3.00'),
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

    def test_perfect_score(self):
        """Test scoring when all answers are correct"""
        # Submit all correct answers
        answers = []
        for q in self.questions:
            correct_choice = q.choices.filter(is_correct=True).first()
            answers.append({
                'question_id': q.id,
                'choice_id': correct_choice.id
            })
            
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        
        # Check redirect to results
        self.assertEqual(response.status_code, 302)
        
        # Verify attempt score
        attempt = QuizAttempt.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.score, 100.0)
        self.assertEqual(attempt.metadata['correct_answers'], 3)
        self.assertEqual(attempt.metadata['earned_points'], 6.0)
        
        # Verify difficulty stats
        diff_stats = attempt.metadata['difficulty_stats']
        self.assertEqual(diff_stats['easy']['correct'], 1)
        self.assertEqual(diff_stats['medium']['correct'], 1)
        self.assertEqual(diff_stats['hard']['correct'], 1)

    def test_partial_score(self):
        """Test scoring when some answers are incorrect"""
        # Submit mixed answers (correct easy, wrong medium, correct hard)
        answers = []
        for q in self.questions:
            if q.difficulty == 'medium':
                choice = q.choices.filter(is_correct=False).first()
            else:
                choice = q.choices.filter(is_correct=True).first()
            answers.append({
                'question_id': q.id,
                'choice_id': choice.id
            })
            
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        
        # Check redirect to results
        self.assertEqual(response.status_code, 302)
        
        # Verify attempt score
        attempt = QuizAttempt.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.score, 66.67)  # (4 points out of 6)
        self.assertEqual(attempt.metadata['correct_answers'], 2)
        self.assertEqual(attempt.metadata['earned_points'], 4.0)
        
        # Verify difficulty stats
        diff_stats = attempt.metadata['difficulty_stats']
        self.assertEqual(diff_stats['easy']['correct'], 1)
        self.assertEqual(diff_stats['medium']['correct'], 0)
        self.assertEqual(diff_stats['hard']['correct'], 1)

    def test_zero_score(self):
        """Test scoring when all answers are incorrect"""
        # Submit all wrong answers
        answers = []
        for q in self.questions:
            wrong_choice = q.choices.filter(is_correct=False).first()
            answers.append({
                'question_id': q.id,
                'choice_id': wrong_choice.id
            })
            
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        
        # Check redirect to results
        self.assertEqual(response.status_code, 302)
        
        # Verify attempt score
        attempt = QuizAttempt.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.score, 0.0)
        self.assertEqual(attempt.metadata['correct_answers'], 0)
        self.assertEqual(attempt.metadata['earned_points'], 0.0)
        
        # Verify difficulty stats
        diff_stats = attempt.metadata['difficulty_stats']
        self.assertEqual(diff_stats['easy']['correct'], 0)
        self.assertEqual(diff_stats['medium']['correct'], 0)
        self.assertEqual(diff_stats['hard']['correct'], 0)

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
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        
        # Check bad request response
        self.assertEqual(response.status_code, 400)
        
        # Verify attempt not completed
        attempt = QuizAttempt.objects.get(id=self.attempt.id)
        self.assertIsNone(attempt.completed_at)
        self.assertIsNone(attempt.score)
