"""
Tests for quiz views.
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.db import transaction
from ..models import Quiz, Question, Choice, QuizAttempt, UserAnswer
from datetime import timedelta
import json

User = get_user_model()

class QuizViewsTest(TestCase):
    """Test cases for quiz views."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            is_active=True,
            passing_score=80.0
        )
        
        # Create test question
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='What is the capital of France?',
            explanation='Paris is the capital of France',
            order=1
        )
        
        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Paris',
            is_correct=True,
            explanation='Correct! Paris is the capital of France.'
        )
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text='London',
            is_correct=False,
            explanation='Incorrect. London is the capital of the UK.'
        )
        
        # Clear cache before each test
        cache.clear()
    
    def test_quiz_list_view(self):
        """Test quiz list view displays active quizzes."""
        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_list.html')
        self.assertContains(response, 'Test Quiz')
        self.assertContains(response, 'Test Description')
        
        # Test pagination
        for i in range(15):
            Quiz.objects.create(
                title=f'Quiz {i}',
                description=f'Description {i}',
                is_active=True
            )
        
        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(len(response.context['quizzes']), 10)  # Default page size
        self.assertTrue(response.context['has_next'])
    
    def test_quiz_list_custom_pagination(self):
        """Test quiz list with custom pagination setting."""
        for i in range(7):
            Quiz.objects.create(
                title=f'Quiz {i+2}',
                description=f'Description {i+2}',
                is_active=True
            )
        
        with self.settings(QUIZZES_PER_PAGE=5):
            response = self.client.get(reverse('quiz:quiz_list'))
            self.assertEqual(len(response.context['quizzes']), 5)
            self.assertTrue(response.context['has_next'])
    
    def test_quiz_detail_view(self):
        """Test quiz detail view displays quiz information."""
        response = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_detail.html')
        self.assertContains(response, 'Test Quiz')
        self.assertContains(response, 'Test Description')
        self.assertContains(response, 'What is the capital of France?')
    
    def test_quiz_detail_caching(self):
        """Test quiz detail view caching."""
        # First request should hit the database
        with self.assertNumQueries(2):  # One for quiz, one for questions
            response1 = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
            self.assertEqual(response1.status_code, 200)
        
        # Second request should use cache
        with self.assertNumQueries(0):
            response2 = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
            self.assertEqual(response2.status_code, 200)
    
    def test_quiz_start_view(self):
        """Test starting a quiz."""
        response = self.client.get(reverse('quiz:start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to take_quiz
        
        # Check attempt was created
        attempt = QuizAttempt.objects.get(user=self.user, quiz=self.quiz)
        self.assertIsNotNone(attempt)
        self.assertIsNone(attempt.completed_at)
    
    def test_quiz_submit_view(self):
        """Test submitting a quiz."""
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:submit_quiz', args=[self.quiz.id]),
            {'answers': [f'{self.question.id}_{self.correct_choice.id}']}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirects to results
        
        # Check answers were saved
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)
        self.assertEqual(attempt.answers.count(), 1)
        self.assertEqual(attempt.score, 100.0)
    
    def test_quiz_results_view(self):
        """Test viewing quiz results."""
        # Create completed attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=5),
            completed_at=timezone.now(),
            score=100.0
        )
        
        # Create answer
        UserAnswer.objects.create(
            attempt=attempt,
            question=self.question,
            choice=self.correct_choice
        )
        
        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_results.html')
        self.assertEqual(response.context['score'], 100.0)
        self.assertTrue(response.context['passed'])
    
    def test_quiz_results_query_optimization(self):
        """Test quiz results view query optimization."""
        # Create completed attempt with answer
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=5),
            completed_at=timezone.now(),
            score=100.0
        )
        
        UserAnswer.objects.create(
            attempt=attempt,
            question=self.question,
            choice=self.correct_choice
        )
        
        # Should only make 2 queries: one for attempt and one for answers
        with self.assertNumQueries(2):
            response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
            self.assertEqual(response.status_code, 200)
    
    def test_quiz_timeout(self):
        """Test quiz timeout handling."""
        # Create an attempt that's timed out
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=31)  # Default timeout is 30 minutes
        )
        
        # Try to submit the quiz
        response = self.client.post(
            reverse('quiz:submit_quiz', args=[self.quiz.id]),
            {'answers': [f'{self.question.id}_{self.correct_choice.id}']}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirects to results
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('time limit exceeded' in str(msg).lower() for msg in messages))
        
        # Check attempt was marked as completed
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)
    
    def test_concurrent_quiz_attempt(self):
        """Test that user cannot start a new quiz while another is in progress."""
        # Create another quiz
        quiz2 = Quiz.objects.create(
            title='Second Quiz',
            description='Another quiz',
            is_active=True
        )

        # Start first quiz
        self.client.get(reverse('quiz:take_quiz', args=[self.quiz.id]))

        # Try to start second quiz
        response = self.client.get(reverse('quiz:take_quiz', args=[quiz2.id]))
        self.assertRedirects(response, reverse('quiz:quiz_list'))
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('another quiz in progress' in str(msg) for msg in messages))

    def test_quiz_submission(self):
        """Test quiz submission and scoring."""
        # Start quiz
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )

        # Submit quiz with correct answer
        response = self.client.post(
            reverse('quiz:submit_quiz', args=[self.quiz.id]),
            data={f'question_{self.question.id}': self.correct_choice.id}
        )
        self.assertRedirects(response, reverse('quiz:quiz_results', args=[self.quiz.id]))

        # Verify attempt was scored correctly
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 100.0)
        self.assertIsNotNone(attempt.completed_at)

    def test_quiz_results_view(self):
        """Test quiz results view displays correct information."""
        # Create completed attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=5),
            completed_at=timezone.now(),
            score=100.0
        )

        # Create user answer
        UserAnswer.objects.create(
            attempt=attempt,
            question=self.question,
            choice=self.correct_choice
        )

        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quiz_results.html')
        self.assertContains(response, 'Test Quiz')
        self.assertContains(response, '100.0')  # Score should be displayed

    def test_inactive_quiz_access(self):
        """Test that inactive quizzes cannot be accessed."""
        self.quiz.is_active = False
        self.quiz.save()

        response = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('quiz:take_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 404)

    def test_quiz_completion_time(self):
        """Test that quiz completion time is recorded correctly."""
        start_time = timezone.now() - timedelta(minutes=10)
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=start_time
        )

        response = self.client.post(
            reverse('quiz:submit_quiz', args=[self.quiz.id]),
            data={f'question_{self.question.id}': self.correct_choice.id}
        )

        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.time_taken)
        self.assertTrue(attempt.time_taken.total_seconds() > 0)
        self.assertTrue(attempt.time_taken.total_seconds() < timedelta(minutes=11).total_seconds())

    def test_quiz_list_view_pagination(self):
        """Test quiz list view pagination."""
        # Create 15 quizzes
        for i in range(15):
            Quiz.objects.create(
                title=f'Quiz {i+2}',  # +2 because we already have one quiz
                description=f'Description {i+2}',
                is_active=True
            )

        # Test first page
        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 10)  # Default items per page
        self.assertTrue(response.context['has_next'])
        self.assertFalse(response.context['has_previous'])

        # Test second page
        response = self.client.get(f"{reverse('quiz:quiz_list')}?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 6)  # Remaining items
        self.assertFalse(response.context['has_next'])
        self.assertTrue(response.context['has_previous'])

    @override_settings(QUIZZES_PER_PAGE=5)
    def test_quiz_list_custom_pagination(self):
        """Test quiz list with custom pagination setting."""
        for i in range(7):
            Quiz.objects.create(
                title=f'Quiz {i+2}',
                description=f'Description {i+2}',
                is_active=True
            )

        response = self.client.get(reverse('quiz:quiz_list'))
        self.assertEqual(len(response.context['quizzes']), 5)

    def test_quiz_list_database_error(self):
        """Test quiz list view handles database errors gracefully."""
        with transaction.atomic():
            # Force a database error by creating an invalid quiz
            Quiz.objects.create(title='')  # This should fail
            
            response = self.client.get(reverse('quiz:quiz_list'))
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any('error occurred' in str(msg) for msg in messages))

    def test_quiz_detail_caching(self):
        """Test quiz detail view caching."""
        # First request should hit the database
        with self.assertNumQueries(2):  # One for quiz, one for questions
            response1 = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
            self.assertEqual(response1.status_code, 200)

        # Second request should use cache
        with self.assertNumQueries(0):
            response2 = self.client.get(reverse('quiz:quiz_detail', args=[self.quiz.id]))
            self.assertEqual(response2.status_code, 200)

    @override_settings(QUIZ_TIME_LIMIT_MINUTES=15)
    def test_custom_time_limit(self):
        """Test custom quiz time limit setting."""
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=16)
        )

        response = self.client.get(reverse('quiz:take_quiz', args=[self.quiz.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('timed out' in str(msg) for msg in messages))

    def test_concurrent_attempt_locking(self):
        """Test concurrent quiz attempt locking."""
        # Start first quiz
        with transaction.atomic():
            response1 = self.client.get(reverse('quiz:take_quiz', args=[self.quiz.id]))
            self.assertEqual(response1.status_code, 200)

            # Try to start same quiz concurrently
            response2 = self.client.get(reverse('quiz:take_quiz', args=[self.quiz.id]))
            self.assertEqual(response2.status_code, 200)
            messages = list(get_messages(response2.wsgi_request))
            self.assertFalse(any('error' in str(msg) for msg in messages))

    def test_quiz_submission_validation(self):
        """Test quiz submission input validation."""
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )

        # Test invalid choice ID
        response = self.client.post(
            reverse('quiz:submit_quiz', args=[self.quiz.id]),
            data={f'question_{self.question.id}': 999999}
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('error occurred' in str(msg) for msg in messages))

        # Test missing answers
        response = self.client.post(
            reverse('quiz:submit_quiz', args=[self.quiz.id]),
            data={}
        )
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 0)

    def test_quiz_results_query_optimization(self):
        """Test quiz results view query optimization."""
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=5),
            completed_at=timezone.now(),
            score=100.0
        )

        UserAnswer.objects.create(
            attempt=attempt,
            question=self.question,
            choice=self.correct_choice
        )

        # Should only make 2 queries: one for attempt and one for answers
        with self.assertNumQueries(2):
            response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
            self.assertEqual(response.status_code, 200)

    def test_quiz_results_error_handling(self):
        """Test quiz results view error handling."""
        # Try to view results for non-existent quiz
        response = self.client.get(reverse('quiz:quiz_results', args=[99999]))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('error occurred' in str(msg) for msg in messages))
        self.assertRedirects(response, reverse('quiz:quiz_list'))

    def test_passing_score_validation(self):
        """Test passing score validation in results."""
        # Create attempt with score just below passing
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=5),
            completed_at=timezone.now(),
            score=79.9
        )

        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['passed'])

        # Update score to passing
        attempt.score = 80.0
        attempt.save()

        response = self.client.get(reverse('quiz:quiz_results', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['passed'])

    def test_calculate_score_no_questions(self):
        """Test score calculation for quiz with no questions."""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            is_active=True,
            passing_score=80.0
        )
        score_data = quiz.calculate_score()
        
        self.assertEqual(score_data['total_questions'], 0)
        self.assertEqual(score_data['correct_answers'], 0)
        self.assertEqual(score_data['score'], 0)
        self.assertFalse(score_data['passed'])
        self.assertEqual(score_data['required_to_pass'], float(quiz.passing_score))

    def test_calculate_score_with_questions(self):
        """Test score calculation with questions and correct answers."""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            is_active=True,
            passing_score=75.0
        )
        
        # Create two questions
        q1 = Question.objects.create(
            quiz=quiz,
            text='What is the capital of France?',
            explanation='Paris is the capital of France',
            order=1
        )
        q2 = Question.objects.create(
            quiz=quiz,
            text='What is the capital of Germany?',
            explanation='Berlin is the capital of Germany',
            order=2
        )
        
        # Add correct and incorrect choices
        Choice.objects.create(
            question=q1,
            text='Paris',
            is_correct=True,
            explanation='Correct! Paris is the capital of France.'
        )
        Choice.objects.create(
            question=q1,
            text='London',
            is_correct=False,
            explanation='Incorrect. London is the capital of the UK.'
        )
        Choice.objects.create(
            question=q2,
            text='Berlin',
            is_correct=True,
            explanation='Correct! Berlin is the capital of Germany.'
        )
        Choice.objects.create(
            question=q2,
            text='Munich',
            is_correct=False,
            explanation='Incorrect. Munich is a city in Germany.'
        )
        
        score_data = quiz.calculate_score()
        
        self.assertEqual(score_data['total_questions'], 2)
        self.assertEqual(score_data['correct_answers'], 2)
        self.assertEqual(score_data['score'], 100.0)
        self.assertTrue(score_data['passed'])
        self.assertEqual(score_data['required_to_pass'], 75.0)

    def test_calculate_score_for_attempt(self):
        """Test score calculation for a specific quiz attempt."""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            is_active=True,
            passing_score=70.0
        )
        
        # Create questions and choices
        q1 = Question.objects.create(
            quiz=quiz,
            text='What is the capital of France?',
            explanation='Paris is the capital of France',
            order=1
        )
        q2 = Question.objects.create(
            quiz=quiz,
            text='What is the capital of Germany?',
            explanation='Berlin is the capital of Germany',
            order=2
        )
        
        c1_correct = Choice.objects.create(
            question=q1,
            text='Paris',
            is_correct=True,
            explanation='Correct! Paris is the capital of France.'
        )
        c1_wrong = Choice.objects.create(
            question=q1,
            text='London',
            is_correct=False,
            explanation='Incorrect. London is the capital of the UK.'
        )
        c2_correct = Choice.objects.create(
            question=q2,
            text='Berlin',
            is_correct=True,
            explanation='Correct! Berlin is the capital of Germany.'
        )
        c2_wrong = Choice.objects.create(
            question=q2,
            text='Munich',
            is_correct=False,
            explanation='Incorrect. Munich is a city in Germany.'
        )
        
        # Create attempt with one correct and one wrong answer
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=quiz,
            started_at=timezone.now()
        )
        UserAnswer.objects.create(
            attempt=attempt,
            question=q1,
            choice=c1_correct  # Correct
        )
        UserAnswer.objects.create(
            attempt=attempt,
            question=q2,
            choice=c2_wrong    # Wrong
        )
        
        score_data = quiz.calculate_score(attempt=attempt)
        
        self.assertEqual(score_data['total_questions'], 2)
        self.assertEqual(score_data['correct_answers'], 1)
        self.assertEqual(score_data['score'], 50.0)
        self.assertFalse(score_data['passed'])
        self.assertEqual(score_data['required_to_pass'], 70.0)

    def test_calculate_score_custom_passing_score(self):
        """Test score calculation with custom passing score."""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            is_active=True,
            passing_score=90.0
        )
        
        # Create question with correct answer
        question = Question.objects.create(
            quiz=quiz,
            text='What is the capital of France?',
            explanation='Paris is the capital of France',
            order=1
        )
        Choice.objects.create(
            question=question,
            text='Paris',
            is_correct=True,
            explanation='Correct! Paris is the capital of France.'
        )
        Choice.objects.create(
            question=question,
            text='London',
            is_correct=False,
            explanation='Incorrect. London is the capital of the UK.'
        )
        
        score_data = quiz.calculate_score()
        
        self.assertEqual(score_data['total_questions'], 1)
        self.assertEqual(score_data['correct_answers'], 1)
        self.assertEqual(score_data['score'], 100.0)
        self.assertTrue(score_data['passed'])
        self.assertEqual(score_data['required_to_pass'], 90.0)

    def test_passing_threshold(self):
        """Test different passing score thresholds."""
        for passing_score, expected_passed in [
            (60.0, True),
            (70.0, True),
            (80.0, False),
            (90.0, False),
        ]:
            quiz = Quiz.objects.create(
                title='Test Quiz',
                description='Test Description',
                is_active=True,
                passing_score=passing_score
            )
            
            # Create 4 questions
            questions = [Question.objects.create(
                quiz=quiz,
                text=f'Question {i+1}',
                explanation=f'Explanation {i+1}',
                order=i+1
            ) for i in range(4)]
            
            # Add choices to each question
            for q in questions:
                Choice.objects.create(
                    question=q,
                    text='Correct answer',
                    is_correct=True,
                    explanation='Correct!'
                )
                Choice.objects.create(
                    question=q,
                    text='Wrong answer',
                    is_correct=False,
                    explanation='Incorrect.'
                )
            
            # Create attempt with 3 correct answers (75% score)
            attempt = QuizAttempt.objects.create(
                user=self.user,
                quiz=quiz,
                started_at=timezone.now()
            )
            
            # Answer first 3 questions correctly, last one incorrectly
            for i, q in enumerate(questions):
                choice = q.choices.filter(is_correct=(i < 3)).first()
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=q,
                    choice=choice
                )
            
            score_data = quiz.calculate_score(attempt=attempt)
            
            self.assertEqual(score_data['score'], 75.0)
            self.assertEqual(score_data['passed'], expected_passed)
            self.assertEqual(score_data['required_to_pass'], passing_score)
