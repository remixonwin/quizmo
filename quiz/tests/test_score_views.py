"""
Tests for quiz score views and UI elements.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from quiz.models import Quiz, Question, Choice, QuizAttempt, UserAnswer
from decimal import Decimal
import json

User = get_user_model()

class QuizScoreViewTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Quiz Description',
            passing_score=70.0,
            time_limit=30,
            is_active=True,
            randomize_questions=True,
            show_answers=True
        )
        
        # Create questions with choices
        self.questions = []
        self.correct_choices = []
        for i in range(5):
            question = Question.objects.create(
                quiz=self.quiz,
                text=f'Test Question {i+1}',
                points=1,
                order=i
            )
            self.questions.append(question)
            
            # Create choices for each question
            correct_choice = Choice.objects.create(
                question=question,
                text=f'Correct Answer {i+1}',
                is_correct=True,
                order=i*2
            )
            self.correct_choices.append(correct_choice)
            
            Choice.objects.create(
                question=question,
                text=f'Wrong Answer {i+1}',
                is_correct=False,
                order=i*2+1
            )
        
        # Clear cache
        cache.clear()

    def create_quiz_attempt(self, correct_answers=3):
        """Helper to create a quiz attempt with specified number of correct answers."""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            started_at=timezone.now(),
            completed_at=timezone.now()
        )
        
        # Calculate score
        score = (correct_answers / len(self.questions)) * 100
        attempt.score = score
        attempt.save()
        
        for i, question in enumerate(self.questions):
            is_correct = i < correct_answers
            choice = self.correct_choices[i] if is_correct else question.choices.filter(is_correct=False).first()
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                choice=choice
            )
        
        return attempt

    def test_quiz_results_view_requires_login(self):
        """Test that quiz results view requires login."""
        # Create a completed attempt first
        attempt = self.create_quiz_attempt()
        
        # Then logout and try to access
        self.client.logout()
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        
        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)

    def test_quiz_results_view_with_no_attempt(self):
        """Test accessing results with no completed attempt."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 404)

    def test_quiz_results_view_with_completed_attempt(self):
        """Test accessing results with a completed attempt."""
        self.client.login(username='testuser', password='testpass123')
        attempt = self.create_quiz_attempt(correct_answers=3)
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_results.html')
        
        # Check context data
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(response.context['attempt'], attempt)
        self.assertEqual(len(response.context['attempt'].answers.all()), 5)
        self.assertEqual(response.context['page_title'], f'Results: {self.quiz.title}')

    def test_quiz_results_caching(self):
        """Test that quiz results are properly cached."""
        self.client.login(username='testuser', password='testpass123')
        attempt = self.create_quiz_attempt(correct_answers=3)
        cache_key = f'quiz_results_{self.quiz.id}_{self.user.id}'
        
        # First request should hit the database
        with self.assertNumQueries(6):  # Session, User, Quiz, Attempt+Quiz, Answers, Choices
            response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
            self.assertEqual(response.status_code, 200)
        
        # Second request should still need session and user queries
        with self.assertNumQueries(2):  # Session and User queries are always needed
            response2 = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        
        self.assertEqual(response2.status_code, 200)
        
        # Clear cache and verify queries are made again
        cache.delete(cache_key)
        with self.assertNumQueries(5):  # Session, User, Attempt+Quiz, Answers, Choices
            response3 = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response3.status_code, 200)

    def test_quiz_results_ui_elements(self):
        """Test that all required UI elements are present in the response."""
        self.client.login(username='testuser', password='testpass123')
        attempt = self.create_quiz_attempt(correct_answers=3)
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        
        content = response.content.decode()
        
        # Check basic page structure
        self.assertInHTML('<h2 class="h4 mb-0">Quiz Results</h2>', content)
        self.assertInHTML(f'<h3>{self.quiz.title}</h3>', content)
        
        # Check score display
        self.assertIn('score-display', content)
        self.assertIn('progress-bar', content)
        
        # Check statistics
        self.assertIn('Total Questions', content)
        self.assertIn('Correct Answers', content)
        self.assertIn('Required to Pass', content)
        
        # Check question review section
        self.assertIn('Question Review', content)
        self.assertIn('Your Answer:', content)
        
        # Check navigation buttons
        self.assertIn('Back to Quiz List', content)
        self.assertIn('Try Again', content)

    def test_quiz_results_pass_fail_status(self):
        """Test that pass/fail status is correctly displayed."""
        self.client.login(username='testuser', password='testpass123')
        
        # Test passing case (4/5 = 80% > 70% pass mark)
        passing_attempt = self.create_quiz_attempt(correct_answers=4)
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertIn('Congratulations! You Passed!', response.content.decode())
        
        # Clear cache between attempts
        cache.clear()
        
        # Test failing case (2/5 = 40% < 70% pass mark)
        failing_attempt = self.create_quiz_attempt(correct_answers=2)
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertIn('Not Passed', response.content.decode())

    def test_quiz_results_score_calculation(self):
        """Test that scores are calculated correctly."""
        self.client.login(username='testuser', password='testpass123')
        attempt = self.create_quiz_attempt(correct_answers=3)
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        
        content = response.content.decode()
        self.assertIn('60.0%', content)  # 3 correct out of 5 = 60%
        self.assertEqual(attempt.score, 60.0)

    def test_quiz_results_explanation_display(self):
        """Test that question explanations are displayed correctly."""
        self.client.login(username='testuser', password='testpass123')
        
        # Add explanation to a question
        self.questions[0].explanation = "This is a test explanation"
        self.questions[0].save()
        
        attempt = self.create_quiz_attempt(correct_answers=3)
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        
        content = response.content.decode()
        self.assertIn('This is a test explanation', content)

    def test_quiz_results_with_invalid_quiz(self):
        """Test accessing results for a non-existent quiz."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:quiz_results', args=[999]))
        self.assertEqual(response.status_code, 404)
