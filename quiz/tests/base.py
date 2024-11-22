"""
Base test class for quiz tests.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from quiz.models import Quiz, Question, Choice, QuizAttempt
from django.utils import timezone
from django.conf import settings
import os
import tempfile
import shutil
from PIL import Image

class QuizTestCase(TestCase):
    """Base test case for quiz tests."""
    
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
            draw = Image.ImageDraw.Draw(image)
            draw.text((10, 40), image_name.replace('.jpg', ''), fill='black')
            image.save(image_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        super().tearDownClass()
        # Remove the temp directory and all its contents
        shutil.rmtree(cls.temp_dir)

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        # Create test user
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        # Create test admin
        cls.test_admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )

        # Create test quiz
        cls.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            passing_score=80.0
        )

        # Create test questions with images
        cls.questions = []
        cls.correct_choices = []
        for i in range(5):
            # Use road sign images cyclically
            image_name = cls.road_sign_images[i % len(cls.road_sign_images)]
            image_path = f'question_images/{image_name}'
            
            question = Question.objects.create(
                quiz=cls.quiz,
                text=f'What does this road sign mean? {i+1}',
                order=i,
                points=1,
                image=image_path
            )
            cls.questions.append(question)

            # Create choices for each question (1 correct, 3 incorrect)
            correct_choice = Choice.objects.create(
                question=question,
                text=f'Correct Answer {i+1}',
                is_correct=True,
                order=1
            )
            cls.correct_choices.append(correct_choice)

            # Create incorrect choices
            for j in range(3):
                Choice.objects.create(
                    question=question,
                    text=f'Wrong Answer {i+1}-{j+1}',
                    is_correct=False,
                    order=j+2
                )

    def create_quiz_attempt(self, correct_answers=0):
        """Create a quiz attempt with specified number of correct answers."""
        attempt = QuizAttempt.objects.create(
            user=self.test_user,
            quiz=self.quiz,
            started_at=timezone.now()
        )

        # Submit answers
        for i, question in enumerate(self.questions[:correct_answers]):
            attempt.answers.create(
                question=question,
                choice=self.correct_choices[i]
            )

        return attempt
