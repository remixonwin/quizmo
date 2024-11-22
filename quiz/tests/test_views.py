"""
Tests for quiz views.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quiz.tests.base import QuizTestCase
from quiz.models import Quiz, Question, Choice, QuizAttempt

class QuizViewTests(QuizTestCase):
    """Test quiz views."""

    def test_quiz_list_view(self):
        """Test the quiz list view"""
        # Login required for quiz list
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_list.html')
        
        # Check if quiz is in context
        self.assertIn(self.quiz, response.context['quizzes'])

    def test_quiz_detail_view(self):
        """Test the quiz detail view"""
        # Login required for quiz detail
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.get(
            reverse('quiz:quiz_detail', kwargs={'pk': self.quiz.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_detail.html')
        
        # Check quiz context
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(len(response.context['questions']), 5)

    def test_quiz_start_view(self):
        """Test starting a quiz"""
        # Login required for starting quiz
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.post(
            reverse('quiz:quiz_start', kwargs={'pk': self.quiz.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirects to quiz attempt
        
        # Check that attempt was created
        self.assertTrue(
            QuizAttempt.objects.filter(
                quiz=self.quiz,
                user=self.test_user
            ).exists()
        )

    def test_quiz_attempt_view(self):
        """Test quiz attempt view"""
        # Login required for quiz attempt
        self.client.login(username=self.test_user.username, password='testpass123')
        
        # Create attempt
        attempt = self.create_quiz_attempt()
        
        response = self.client.get(
            reverse('quiz:quiz_attempt', kwargs={'pk': attempt.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_attempt.html')
        
        # Check attempt context
        self.assertEqual(response.context['attempt'], attempt)
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(len(response.context['questions']), 5)

    def test_quiz_submit_view(self):
        """Test submitting quiz answers"""
        # Login required for submitting quiz
        self.client.login(username=self.test_user.username, password='testpass123')
        
        # Create attempt
        attempt = self.create_quiz_attempt()
        
        # Get correct answers for each question
        answers = {}
        for question in self.questions:
            correct_choice = Choice.objects.get(
                question=question,
                is_correct=True
            )
            answers[f'question_{question.pk}'] = correct_choice.pk
        
        response = self.client.post(
            reverse('quiz:quiz_submit', kwargs={'pk': attempt.pk}),
            data=answers
        )
        self.assertEqual(response.status_code, 302)  # Redirects to results
        
        # Refresh attempt from db
        attempt.refresh_from_db()
        self.assertTrue(attempt.completed_at)
        self.assertEqual(attempt.score, 100.0)

    def test_quiz_results_view(self):
        """Test quiz results view"""
        # Login required for viewing results
        self.client.login(username=self.test_user.username, password='testpass123')
        
        # Create and complete attempt
        attempt = self.create_quiz_attempt(correct_answers=3)
        attempt.complete()
        
        response = self.client.get(
            reverse('quiz:quiz_results', kwargs={'pk': attempt.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_results.html')
        
        # Check results context
        self.assertEqual(response.context['attempt'], attempt)
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(response.context['score'], 60.0)  # 3/5 correct

class QuizAuthTests(QuizTestCase):
    """Test quiz view authentication."""

    def test_login_required(self):
        """Test that views require login"""
        # List of URL names that require login
        protected_urls = [
            'quiz:quiz_list',
            'quiz:quiz_detail',
            'quiz:quiz_start',
            'quiz:quiz_attempt',
            'quiz:quiz_submit',
            'quiz:quiz_results'
        ]
        
        # Test each protected URL
        for url_name in protected_urls:
            # For URLs that need parameters, use the quiz pk
            kwargs = {}
            if 'pk' in url_name:
                kwargs['pk'] = self.quiz.pk
            
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/accounts/login/'))

class QuizProgressTests(QuizTestCase):
    """Test quiz progress tracking."""

    def test_quiz_progress(self):
        """Test tracking quiz progress"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        # Create multiple attempts
        attempts = []
        scores = [100.0, 60.0, 80.0]
        for score in scores:
            correct = int((score / 100.0) * 5)  # 5 questions total
            attempt = self.create_quiz_attempt(correct_answers=correct)
            attempt.complete()
            attempts.append(attempt)
        
        # Check progress view
        response = self.client.get(reverse('quiz:quiz_progress'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_progress.html')
        
        # Verify progress data
        progress = response.context['progress']
        self.assertEqual(len(progress['attempts']), 3)
        self.assertEqual(progress['average_score'], 80.0)
        self.assertEqual(progress['best_score'], 100.0)
        self.assertEqual(progress['total_attempts'], 3)

class QuizAPITests(QuizTestCase):
    """Test quiz API views."""

    def test_quiz_api_list(self):
        """Test quiz list API"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.get(reverse('quiz:api_quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Check response data
        data = response.json()
        self.assertEqual(len(data['quizzes']), 1)
        self.assertEqual(data['quizzes'][0]['title'], self.quiz.title)

    def test_quiz_api_detail(self):
        """Test quiz detail API"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.get(
            reverse('quiz:api_quiz_detail', kwargs={'pk': self.quiz.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Check response data
        data = response.json()
        self.assertEqual(data['title'], self.quiz.title)
        self.assertEqual(len(data['questions']), 5)

    def test_quiz_api_submit(self):
        """Test quiz submission API"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        # Create attempt
        attempt = self.create_quiz_attempt()
        
        # Get correct answers
        answers = {}
        for question in self.questions:
            correct_choice = Choice.objects.get(
                question=question,
                is_correct=True
            )
            answers[str(question.pk)] = correct_choice.pk
        
        response = self.client.post(
            reverse('quiz:api_quiz_submit', kwargs={'pk': attempt.pk}),
            data=answers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        data = response.json()
        self.assertEqual(data['score'], 100.0)
        self.assertTrue(data['passed'])
        self.assertEqual(data['correct_answers'], 5)
