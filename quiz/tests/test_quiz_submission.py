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
from unittest import mock
import tempfile
import shutil
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os

User = get_user_model()

class QuizSubmissionTests(TestCase):
    """Test quiz submission and scoring functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        # Create a temp directory for media files during tests
        cls.temp_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = cls.temp_dir
        
        # Create the question_images directory
        os.makedirs(os.path.join(cls.temp_dir, 'question_images'), exist_ok=True)
        
        # Create test road sign images
        cls.road_sign_images = [
            'stop_sign.jpg',
            'yield.jpg',
            'speed_70.jpg',
            'no_left_turn.jpg',
            'no_right_turn.jpg'
        ]
        
        for image_name in cls.road_sign_images:
            image_path = os.path.join(cls.temp_dir, 'question_images', image_name)
            # Create a small test image
            image = Image.new('RGB', (100, 100), 'white')
            draw = ImageDraw.Draw(image)
            draw.text((10, 40), image_name.replace('.jpg', ''), fill='black')
            image.save(image_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        super().tearDownClass()
        # Remove the temp directory and all its contents
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """Set up test data."""
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Get CSRF token
        response = self.client.get(reverse('quiz:quiz_list'))
        self.csrf_token = response.cookies['csrftoken'].value
        
        # Create a quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            is_active=True,
            passing_score=70.0,
            time_limit=30  # 30 minutes
        )
        
        # Create test questions with images
        self.questions = []
        self.correct_choices = []
        for i in range(40):
            # Use road sign images cyclically
            image_name = self.road_sign_images[i % len(self.road_sign_images)]
            image_path = f'question_images/{image_name}'
            
            question = Question.objects.create(
                quiz=self.quiz,
                text=f'What does this road sign mean? {i+1}',
                order=i+1,
                points=1.0,
                image=image_path
            )
            self.questions.append(question)
            
            # Add correct choice
            correct_choice = Choice.objects.create(
                question=question,
                text=f'Correct Answer {i+1}',
                is_correct=True,
                order=1
            )
            self.correct_choices.append(correct_choice)
            
            # Add wrong choices
            for j in range(3):
                Choice.objects.create(
                    question=question,
                    text=f'Wrong Answer {i+1}-{j+1}',
                    is_correct=False,
                    order=j+2
                )

    def test_quiz_submission_perfect_score(self):
        """Test quiz submission with all correct answers."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[i].id
            })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 302)  # Redirect to results
        self.assertTrue(response.url.startswith(reverse('quiz:quiz_results', args=[self.quiz.id])))
        
        # Check attempt score
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, Decimal('100.0'))

    def test_quiz_submission_partial_score(self):
        """Test quiz submission with mix of correct and wrong answers."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            if i < 20:  # First 20 correct, last 20 wrong
                answers.append({
                    'question_id': question.id,
                    'choice_id': self.correct_choices[i].id
                })
            else:
                answers.append({
                    'question_id': question.id,
                    'choice_id': Choice.objects.get(question=question, order=2).id
                })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 302)  # Redirect to results
        self.assertTrue(response.url.startswith(reverse('quiz:quiz_results', args=[self.quiz.id])))
        
        # Check attempt score
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, Decimal('50.0'))

    def test_quiz_submission_validation(self):
        """Test validation of quiz submissions."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data with missing answer
        answers = []
        for i, question in enumerate(self.questions):
            if i > 0:  # Skip first question
                answers.append({
                    'question_id': question.id,
                    'choice_id': self.correct_choices[i].id
                })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)  # Error response
        self.assertIn('error', response.content.decode('utf-8'))
        
        # Prepare submission data with invalid choice ID
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': 99999  # Invalid choice ID
            })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)  # Error response
        self.assertIn('error', response.content.decode('utf-8'))

    def test_quiz_submission_time_limit(self):
        """Test quiz submission with time limit validation."""
        # Create a fixed timestamp for consistent testing
        start_time = timezone.now()
        current_time = start_time + timezone.timedelta(minutes=31)  # 31 minutes later
        
        # Create a quiz attempt with start time 31 minutes ago
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=start_time,  # Started at our fixed start time
            completed_at=None
        )
        
        # Mock timezone.now() to return our fixed current time
        with mock.patch('quiz.views.quiz.submit.timezone.now', return_value=current_time):
            # Prepare submission data
            answers = []
            for i, question in enumerate(self.questions):
                answers.append({
                    'question_id': question.id,
                    'choice_id': self.correct_choices[i].id
                })
            
            # Submit answers
            response = self.client.post(
                reverse('quiz:quiz_submit', args=[self.quiz.id]),
                data={
                    'answers': json.dumps(answers),
                    'csrfmiddlewaretoken': self.csrf_token,
                    'metadata': json.dumps({
                        'submittedAt': timezone.now().isoformat(),
                        'timeZone': 'UTC',
                        'userAgent': 'Mozilla/5.0 (Test)'
                    })
                }
            )
            
            # Check response
            self.assertEqual(response.status_code, 400)  # Error response
            self.assertIn('Time limit', response.content.decode('utf-8'))
            self.assertIn('30 minutes', response.content.decode('utf-8'))

    def test_quiz_submission_with_inactive_questions(self):
        """Test quiz submission handling with inactive questions."""
        # Make some questions inactive
        inactive_questions = self.quiz.questions.all()[:10]
        for question in inactive_questions:
            question.is_active = False
            question.save()
        
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[i].id
            })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 302)  # Redirect to results
        self.assertTrue(response.url.startswith(reverse('quiz:quiz_results', args=[self.quiz.id])))
        
        # Check attempt score
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, Decimal('100.0'))

    def test_invalid_json_data(self):
        """Test submission with invalid JSON data."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Submit with invalid JSON
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': 'invalid json data',
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertIn('Invalid JSON', response_data['error'])

    def test_api_quiz_submission(self):
        """Test quiz submission through API endpoint."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[i].id
            })
        
        # Submit answers to API endpoint
        response = self.client.post(
            reverse('quiz:api_quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=self.csrf_token
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)  # Success JSON response
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('score', data)
        self.assertEqual(data['score'], 100.0)
        self.assertEqual(data['correct_answers'], len(self.questions))
        self.assertEqual(data['total_questions'], len(self.questions))
        
        # Check attempt score in database
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, Decimal('100.0'))

    def test_malformed_metadata(self):
        """Test submission with malformed metadata."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[i].id
            })
        
        # Submit with malformed metadata
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': 'invalid json'
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertIn('Invalid JSON', response_data['error'])
        
    def test_invalid_choice_combinations(self):
        """Test submission with invalid choice combinations."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission with choices from wrong questions
        answers = []
        for i, question in enumerate(self.questions):
            wrong_choice = Choice.objects.exclude(question=question).first()
            answers.append({
                'question_id': question.id,
                'choice_id': wrong_choice.id
            })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertIn('Invalid question or choice ID', response_data['error'])
        
    def test_duplicate_answers(self):
        """Test submission with duplicate answers for the same question."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission with duplicate answers
        answers = []
        question = self.questions[0]
        for _ in range(2):  # Add same answer twice
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[0].id
            })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertIn('Incomplete submission', response_data['error'])
        
    def test_missing_metadata(self):
        """Test submission without metadata."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[i].id
            })
        
        # Submit without metadata
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token
            }
        )
        
        # Check response - should still work with default metadata
        self.assertEqual(response.status_code, 302)  # Redirect to results
        
        # Verify attempt was saved
        attempt = QuizAttempt.objects.latest('id')
        self.assertIsNotNone(attempt.metadata)
        self.assertIn('completion_time', attempt.metadata)
        
    def test_concurrent_submissions(self):
        """Test handling of concurrent submissions for the same quiz."""
        # Create initial quiz attempt
        first_attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Create a second attempt before completing the first
        second_attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[i].id
            })
        
        # Submit answers for both attempts
        response1 = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        response2 = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check responses
        self.assertEqual(response1.status_code, 302)  # First submission succeeds
        self.assertEqual(response2.status_code, 302)  # Second submission also succeeds
        
        # Verify both attempts were completed
        first_attempt.refresh_from_db()
        second_attempt.refresh_from_db()
        self.assertIsNotNone(first_attempt.completed_at)
        self.assertIsNotNone(second_attempt.completed_at)
        self.assertEqual(first_attempt.score, second_attempt.score)

    def test_empty_answers(self):
        """Test submission with empty answers list."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Submit with empty answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps([]),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertIn('No answers provided', response_data['error'])
        
    def test_invalid_question_id(self):
        """Test submission with non-existent question ID."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Get all active questions
        active_questions = self.quiz.questions.filter(is_active=True)
        
        # Prepare answers with non-existent question ID
        answers = []
        for question in active_questions:
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[0].id  # Use first choice for all questions
            })
        
        # Add one more answer with invalid question ID
        answers.append({
            'question_id': 99999,  # Invalid ID
            'choice_id': self.correct_choices[0].id
        })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertIn('Invalid question or choice ID', response_data['error'])
        
    def test_missing_required_fields(self):
        """Test submission with missing required fields in answers."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare answers with missing fields
        answers = []
        for i, question in enumerate(self.questions):
            if i == 0:
                answers.append({'question_id': question.id})  # Missing choice_id
            elif i == 1:
                answers.append({'choice_id': self.correct_choices[i].id})  # Missing question_id
            else:
                answers.append({
                    'question_id': question.id,
                    'choice_id': self.correct_choices[i].id
                })
        
        # Submit answers
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertIn('Invalid answer format', response_data['error'])
        
    def test_api_submission_with_form_data(self):
        """Test API submission with form data instead of JSON."""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        # Prepare submission data
        answers = []
        for i, question in enumerate(self.questions):
            answers.append({
                'question_id': question.id,
                'choice_id': self.correct_choices[i].id
            })
        
        # Submit as form data to API endpoint
        response = self.client.post(
            reverse('quiz:api_quiz_submit', args=[self.quiz.id]),
            data={
                'answers': json.dumps(answers),
                'csrfmiddlewaretoken': self.csrf_token,
                'metadata': json.dumps({
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                })
            },
            HTTP_X_CSRFTOKEN=self.csrf_token
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)  # Should still work
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('score', data)
        self.assertEqual(float(data['score']), 100.0)
