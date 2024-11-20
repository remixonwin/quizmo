from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from quiz.models import Quiz, Question, Choice
from django.utils import timezone
import json
from django.test import override_settings
from django.contrib.messages import get_messages

class QuizViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='A test quiz'
        )
        
        # Create test questions and choices
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test question?'
        )
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct answer',
            is_correct=True
        )
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text='Wrong answer',
            is_correct=False
        )

    def test_quiz_list_view(self):
        """Test the quiz list view."""
        response = self.client.get(reverse('quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_list.html')
        self.assertContains(response, 'Test Quiz')

    def test_quiz_detail_view(self):
        """Test the quiz detail view."""
        response = self.client.get(reverse('quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_detail.html')
        self.assertContains(response, 'Test Quiz')

    def test_take_quiz_authentication(self):
        """Test that quiz taking requires authentication."""
        # Test unauthenticated access
        response = self.client.get(reverse('take_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('take_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)

    def test_concurrent_quiz_attempts(self):
        """Test handling of concurrent quiz attempts."""
        self.client.login(username='testuser', password='testpass123')
        
        # Start first quiz
        self.client.get(reverse('take_quiz', args=[self.quiz.id]))
        
        # Create second quiz
        quiz2 = Quiz.objects.create(title='Test Quiz 2')
        
        # Try to start second quiz
        response = self.client.get(reverse('take_quiz', args=[quiz2.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('another quiz in progress' in str(m) for m in messages))

    def test_quiz_timeout(self):
        """Test quiz timeout functionality."""
        self.client.login(username='testuser', password='testpass123')
        
        # Start quiz with expired time
        session = self.client.session
        session['quiz_start_time'] = (timezone.now() - timezone.timedelta(minutes=61)).isoformat()
        session.save()
        
        # Try to submit quiz
        response = self.client.post(reverse('submit_quiz', args=[self.quiz.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('time limit exceeded' in str(m) for m in messages))

    def test_quiz_submission_and_scoring(self):
        """Test quiz submission and score calculation."""
        self.client.login(username='testuser', password='testpass123')
        
        # Start the quiz first
        self.client.get(reverse('take_quiz', args=[self.quiz.id]))
        
        # Submit quiz with correct answer
        response = self.client.post(
            reverse('submit_quiz', args=[self.quiz.id]),
            data={f'question_{self.question.id}': self.correct_choice.id}
        )
        
        # Check redirect to results
        self.assertRedirects(response, reverse('quiz_results', args=[self.quiz.id]))
        
        # Verify results in session
        results = self.client.session.get(f'quiz_{self.quiz.id}_results')
        self.assertEqual(results['score'], 100.0)
        self.assertTrue(results['passed'])

    def test_quiz_results_view(self):
        """Test the quiz results view."""
        self.client.login(username='testuser', password='testpass123')
        
        # Store test results in session
        session = self.client.session
        session[f'quiz_{self.quiz.id}_results'] = {
            'score': 85.0,
            'passed': True,
            'total_questions': 20,
            'correct_answers': 17
        }
        session.save()
        
        # Access results page
        response = self.client.get(reverse('quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_results.html')
        self.assertContains(response, '85.0')

    def test_session_cleanup(self):
        """Test proper cleanup of session data after quiz completion."""
        self.client.login(username='testuser', password='testpass123')
        
        # Start the quiz first
        self.client.get(reverse('take_quiz', args=[self.quiz.id]))
        
        # Submit quiz
        self.client.post(
            reverse('submit_quiz', args=[self.quiz.id]),
            data={f'question_{self.question.id}': self.correct_choice.id}
        )
        
        # Check session cleanup
        self.assertNotIn('quiz_start_time', self.client.session)
        self.assertNotIn('quiz_in_progress', self.client.session)
        self.assertNotIn('quiz_answers', self.client.session)
