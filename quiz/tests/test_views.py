"""
Tests for quiz views.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta
from quiz.models import Quiz, Question, Choice, QuizAttempt


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
            description='A test quiz',
            is_active=True,
            created_at=timezone.now()
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

    def test_quiz_list_view_unauthenticated(self):
        """Test the quiz list view without authentication."""
        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('quiz:quiz_list'))

    def test_quiz_list_view_authenticated(self):
        """Test the quiz list view with authentication."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_list.html')
        self.assertContains(response, 'Test Quiz')

    def test_quiz_detail_view_unauthenticated(self):
        """Test the quiz detail view without authentication."""
        response = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, 
            '/accounts/login/?next=' + reverse('quiz:quiz_detail', args=[self.quiz.id])
        )

    def test_quiz_detail_view_authenticated(self):
        """Test the quiz detail view with authentication."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_detail.html')
        self.assertContains(response, 'Test Quiz')

    def test_start_quiz_authentication(self):
        """Test that quiz starting requires authentication."""
        # Test unauthenticated access
        response = self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, 
            '/accounts/login/?next=' + reverse('quiz:start_quiz', args=[self.quiz.id])
        )
        
        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/take_quiz.html')

    def test_concurrent_quiz_attempts(self):
        """Test handling of concurrent quiz attempts."""
        self.client.login(username='testuser', password='testpass123')
        
        # Start first quiz
        response = self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        
        # Try to start another quiz while one is in progress
        response = self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 400)  # Bad request, quiz already in progress
        
        # Submit the quiz
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            {'question_{}'.format(self.question.id): self.correct_choice.id}
        )
        self.assertEqual(response.status_code, 302)  # Redirects to results
        self.assertRedirects(response, reverse('quiz:quiz_results', args=[self.quiz.id]))

    def test_quiz_submission(self):
        """Test quiz submission and scoring."""
        self.client.login(username='testuser', password='testpass123')
        
        # Start the quiz
        self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        
        # Submit with correct answer
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            {'question_{}'.format(self.question.id): self.correct_choice.id}
        )
        self.assertEqual(response.status_code, 302)
        
        # Check results
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '100')  # Should show 100% score
        
        # Submit with wrong answer
        self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            {'question_{}'.format(self.question.id): self.wrong_choice.id}
        )
        self.assertEqual(response.status_code, 302)
        
        # Check results
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0')  # Should show 0% score

    def test_quiz_timeout(self):
        """Test quiz timeout handling."""
        self.client.login(username='testuser', password='testpass123')
        
        # Start the quiz
        self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        
        # Get the quiz attempt and set it to have started 31 minutes ago
        attempt = QuizAttempt.objects.get(user=self.user, quiz=self.quiz)
        attempt.started_at = timezone.now() - timedelta(minutes=31)
        attempt.save()
        
        # Try to submit after timeout
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            {'question_{}'.format(self.question.id): self.correct_choice.id}
        )
        self.assertEqual(response.status_code, 400)  # Bad request, quiz timed out


class HelpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_help_page_loads(self):
        """Test that help page loads correctly."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:help'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help.html')

    def test_help_page_context(self):
        """Test that help page has correct context data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:help'))
        self.assertTrue('quick_start' in response.context)
        self.assertTrue('study_materials' in response.context)
        self.assertTrue('study_tips' in response.context)
        self.assertTrue('content' in response.context)

    def test_study_materials_content(self):
        """Test study materials content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:help'))
        study_materials = response.context['study_materials']
        self.assertTrue(len(study_materials) > 0)
        self.assertTrue(all('title' in material for material in study_materials))
        self.assertTrue(all('description' in material for material in study_materials))

    def test_quick_start_content(self):
        """Test quick start guide content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:help'))
        quick_start = response.context['quick_start']
        self.assertTrue(len(quick_start) > 0)
        self.assertTrue(all('title' in guide for guide in quick_start))
        self.assertTrue(all('description' in guide for guide in quick_start))

    def test_faq_content(self):
        """Test FAQ content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/faq.html')

    def test_search_functionality(self):
        """Test help search functionality."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quiz:help') + '?search=test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('search_query' in response.context)
        self.assertEqual(response.context['search_query'], 'test')
