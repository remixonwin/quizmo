"""
Tests for quiz API views.
"""
from django.urls import reverse
from quiz.models import Choice
from quiz.tests.views.base import BaseViewTest

class QuizAPITests(BaseViewTest):
    """Test quiz API views."""

    def test_quiz_api_list(self):
        """Test quiz list API"""
        self.client.login(username=self.test_user.username, password='testpass123')
        
        response = self.client.get(reverse('quiz:api_quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
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
        
        data = response.json()
        self.assertEqual(data['title'], self.quiz.title)
        self.assertEqual(len(data['questions']), 5)

    def test_quiz_api_submit(self):
        """Test quiz submission API"""
        self.client.login(username=self.test_user.username, password='testpass123')
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
        
        data = response.json()
        self.assertEqual(data['score'], 100.0)
        self.assertTrue(data['passed'])
        self.assertEqual(data['correct_answers'], 5)
