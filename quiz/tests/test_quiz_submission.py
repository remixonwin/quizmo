"""
Tests for quiz submission and scoring functionality.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from quiz.models import Quiz, Question, Choice, QuizAttempt, UserAnswer
from decimal import Decimal
import json

User = get_user_model()

class QuizSubmissionTests(TestCase):
    """Test quiz submission and scoring functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create a quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            is_active=True,
            pass_mark=70.0
        )
        
        # Create questions with choices
        self.questions = []
        self.correct_choices = []
        self.wrong_choices = []
        
        for i in range(4):
            question = Question.objects.create(
                quiz=self.quiz,
                text=f'Question {i+1}',
                explanation=f'Explanation {i+1}',
                order=i+1
            )
            self.questions.append(question)
            
            # Add correct choice
            correct = Choice.objects.create(
                question=question,
                text=f'Correct Answer {i+1}',
                is_correct=True,
                explanation=f'This is correct for question {i+1}',
                order=1
            )
            self.correct_choices.append(correct)
            
            # Add wrong choice
            wrong = Choice.objects.create(
                question=question,
                text=f'Wrong Answer {i+1}',
                is_correct=False,
                explanation=f'This is wrong for question {i+1}',
                order=2
            )
            self.wrong_choices.append(wrong)
    
    def test_quiz_submission_perfect_score(self):
        """Test submitting a quiz with all correct answers."""
        # Start quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Create submission data with all correct answers
        answers = []
        for question, choice in zip(self.questions, self.correct_choices):
            answers.append({
                'question_id': question.id,
                'choice_id': choice.id,
                'is_correct': True
            })
            
        # Submit quiz
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        
        # Verify redirect to results
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(f'/quiz/{self.quiz.id}/results/'))
        
        # Verify attempt was scored correctly
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 100.0)
        self.assertTrue(attempt.has_passed)
        self.assertEqual(attempt.answers.count(), 4)
        
        # Verify all answers were recorded correctly
        for answer in attempt.answers.all():
            self.assertTrue(answer.is_correct)
            
    def test_quiz_submission_partial_score(self):
        """Test submitting a quiz with mix of correct and wrong answers."""
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Create submission with 2 correct and 2 wrong answers
        answers = []
        for i, (question, choice) in enumerate(zip(self.questions, self.correct_choices)):
            # First 2 correct, last 2 wrong
            if i < 2:
                answers.append({
                    'question_id': question.id,
                    'choice_id': choice.id,
                    'is_correct': True
                })
            else:
                answers.append({
                    'question_id': question.id,
                    'choice_id': self.wrong_choices[i].id,
                    'is_correct': False
                })
                
        # Submit quiz
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify scoring
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 50.0)  # 2/4 = 50%
        self.assertFalse(attempt.has_passed)  # Below 70% passing threshold
        self.assertEqual(attempt.answers.count(), 4)
        
        # Verify answer correctness
        answers = attempt.answers.order_by('question__order')
        self.assertTrue(answers[0].is_correct)
        self.assertTrue(answers[1].is_correct)
        self.assertFalse(answers[2].is_correct)
        self.assertFalse(answers[3].is_correct)
        
    def test_quiz_submission_validation(self):
        """Test validation of quiz submissions."""
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Test invalid question ID
        answers = [{
            'question_id': 99999,
            'choice_id': self.correct_choices[0].id,
            'is_correct': True
        }]
        
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test invalid choice ID
        answers = [{
            'question_id': self.questions[0].id,
            'choice_id': 99999,
            'is_correct': True
        }]
        
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test missing answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': []}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
    def test_quiz_submission_completion_time(self):
        """Test that completion time is recorded correctly."""
        start_time = timezone.now() - timezone.timedelta(minutes=5)
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=start_time
        )
        
        # Submit all correct answers
        answers = []
        for question, choice in zip(self.questions, self.correct_choices):
            answers.append({
                'question_id': question.id,
                'choice_id': choice.id,
                'is_correct': True
            })
            
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        
        # Verify completion time
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)
        self.assertIsNotNone(attempt.time_taken)
        self.assertTrue(attempt.time_taken >= 300)  # At least 5 minutes
        self.assertTrue(attempt.time_taken <= 301)  # But not much more
