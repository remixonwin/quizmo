from .base import BaseTestCase
from rest_framework import status
from backend.core.models import Quiz, Question, Choice
import base64

class QuizCreateTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.quiz_data = {
            'title': 'Test Quiz',
            'description': 'Test Description',
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

    def create_quiz(self, **kwargs):
        """Helper method to create a quiz"""
        data = {**self.quiz_data, **kwargs}
        return self.client.post('/api/quizzes/', data, format='json')

    def test_create_quiz_success(self):
        response = self.create_quiz()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Choice.objects.count(), 2)

    def test_create_quiz_with_image(self):
        # Test with base64 encoded image
        image_data = base64.b64encode(b"test image data").decode()
        response = self.create_quiz(image=image_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.first().image, image_data)

    def test_quiz_validation(self):
        # Test invalid data cases
        invalid_cases = [
            ({}, "Required fields missing"),
            ({'title': '', 'description': 'Test'}, "Empty title"),
            ({'title': 'Test', 'description': ''}, "Empty description"),
            (
                {
                    'title': 'Test',
                    'description': 'Test',
                    'questions': []
                },
                "No questions"
            )
        ]

        for data, case in invalid_cases:
            response = self.client.post('/api/quizzes/', data, format='json')
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Failed case: {case}"
            )

class QuizAccessTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description', 
            author=self.user
        )

    def test_quiz_authorized_access(self):
        # Test authorized access
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test unauthorized access
        self.client.logout()
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_quiz_deletion(self):
        # Test deletion
        response = self.client.delete(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Quiz.objects.count(), 0)

class QuizUpdateTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            author=self.user
        )

    def test_quiz_update(self):
        # Test update
        update_data = {'title': 'Updated Quiz'}
        response = self.client.patch(
            f'/api/quizzes/{self.quiz.id}/',
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Quiz.objects.get(id=self.quiz.id).title, 'Updated Quiz')

    def test_quiz_concurrent_access(self):
        """Test concurrent access handling"""
        # Create two clients
        client1 = APIClient()
        client2 = APIClient()
        client1.force_authenticate(user=self.user)
        client2.force_authenticate(user=self.user)

        # Create a quiz
        response = client1.post('/api/quizzes/', self.quiz_data, format='json')
        quiz_id = response.data['id']

        # Attempt concurrent updates
        update_data1 = {'title': 'Updated by client 1'}
        update_data2 = {'title': 'Updated by client 2'}
        response1 = client1.patch(f'/api/quizzes/{quiz_id}/', update_data1, format='json')
        response2 = client2.patch(f'/api/quizzes/{quiz_id}/', update_data2, format='json')

        self.assertTrue(
            response1.status_code == status.HTTP_200_OK or 
            response2.status_code == status.HTTP_200_OK
        )

class QuizQuestionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description',
            author=self.user
        )
        self.question_data = {
            'text': 'Test Question',
            'points': 1,
            'choices': [
                {'text': 'Choice 1', 'is_correct': True},
                {'text': 'Choice 2', 'is_correct': False}
            ]
        }

    def test_add_question(self):
        """Test adding a question to a quiz"""
        response = self.client.post(
            f'/api/quizzes/{self.quiz.id}/questions/',
            self.question_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.quiz.questions.count(), 1)