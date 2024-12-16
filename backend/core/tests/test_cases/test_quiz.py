from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from backend.core.models import Quiz, Question, Choice

User = get_user_model()

class QuizCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.quiz_data = {
            'title': 'Test Quiz',
            'description': 'Test Description',
            'author': self.user.id,  # Add author ID
            'questions': [
                {
                    'text': 'Test Question',
                    'points': 1,
                    'choices': [
                        {'text': 'Choice 1', 'is_correct': True},
                        {'text': 'Choice 2', 'is_correct': False}
                    ]
                }
            ]
        }

    def test_create_quiz(self):
        response = self.client.post('/api/quizzes/', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Choice.objects.count(), 2)

    def test_create_quiz_with_missing_title(self):
        self.quiz_data['title'] = ''
        response = self.client.post('/api/quizzes/', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_create_quiz_with_invalid_points(self):
        self.quiz_data['questions'][0]['points'] = -1
        response = self.client.post('/api/quizzes/', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('points', response.data['questions'][0])

    def test_create_quiz_with_no_choices(self):
        self.quiz_data['questions'][0]['choices'] = []
        response = self.client.post('/api/quizzes/', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('choices', response.data)

class QuizAccessTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            author=self.user
        )

    def test_quiz_list(self):
        pass

class QuizUpdateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            author=self.user
        )

    def test_update_quiz(self):
        data = {
            'title': 'Updated Quiz',
            'description': 'Updated Description'
        }
        response = self.client.patch(f'/api/quizzes/{self.quiz.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Updated Quiz')
        self.assertEqual(self.quiz.description, 'Updated Description')

    def test_update_quiz_with_invalid_title(self):
        data = {'title': ''}
        response = self.client.patch(f'/api/quizzes/{self.quiz.id}/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_update_quiz_with_invalid_author(self):
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        data = {'author': new_user.id}
        response = self.client.patch(f'/api/quizzes/{self.quiz.id}/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('author', response.data)

class QuizQuestionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            author=self.user
        )
        self.question_data = {
            'quiz': self.quiz.id,  # Add this line
            'text': 'Test Question',
            'points': 1,
            'choices': [
                {'text': 'Choice 1', 'is_correct': True},
                {'text': 'Choice 2', 'is_correct': False}
            ]
        }

    def test_add_question(self):
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/questions/', self.question_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Choice.objects.count(), 2)

    def test_add_question_with_invalid_text(self):
        self.question_data['text'] = ''
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/questions/', self.question_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('text', response.data)

    def test_add_question_with_no_choices(self):
        self.question_data['choices'] = []
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/questions/', self.question_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('choices', response.data)
