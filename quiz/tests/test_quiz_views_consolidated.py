"""
Consolidated tests for quiz views.
"""
import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta
from quiz.models import UserAnswer

pytestmark = pytest.mark.django_db

class TestQuizViews:
    """Test cases for quiz-related views."""
    
    def test_quiz_list_unauthenticated(self, client):
        """Test the quiz list view without authentication."""
        response = client.get(reverse('quiz:quiz_list'))
        assert response.status_code == 302
        assert '/login/' in response['Location']

    def test_quiz_list_authenticated(self, authenticated_client, quiz_with_questions):
        """Test the quiz list view with authentication."""
        response = authenticated_client.get(reverse('quiz:quiz_list'))
        assert response.status_code == 200
        assert quiz_with_questions.title in str(response.content)

    def test_quiz_detail(self, authenticated_client, quiz_with_questions):
        """Test viewing a specific quiz."""
        response = authenticated_client.get(
            reverse('quiz:quiz_detail', kwargs={'pk': quiz_with_questions.pk})
        )
        assert response.status_code == 200
        assert quiz_with_questions.title in str(response.content)
        assert quiz_with_questions.description in str(response.content)

    def test_start_quiz(self, authenticated_client, quiz_with_questions):
        """Test starting a quiz."""
        response = authenticated_client.post(
            reverse('quiz:start_quiz', kwargs={'pk': quiz_with_questions.pk})
        )
        assert response.status_code == 302
        assert 'take_quiz' in response['Location']

    def test_take_quiz(self, authenticated_client, quiz_attempt):
        """Test taking a quiz."""
        response = authenticated_client.get(
            reverse('quiz:take_quiz', kwargs={'attempt_id': quiz_attempt.pk})
        )
        assert response.status_code == 200
        assert quiz_attempt.quiz.title in str(response.content)

    def test_submit_answer(self, authenticated_client, quiz_attempt):
        """Test submitting an answer."""
        question = quiz_attempt.quiz.question_set.first()
        correct_choice = question.choice_set.filter(is_correct=True).first()
        
        response = authenticated_client.post(
            reverse('quiz:submit_answer', kwargs={'attempt_id': quiz_attempt.pk}),
            {'question': question.pk, 'choice': correct_choice.pk}
        )
        assert response.status_code == 200
        assert UserAnswer.objects.filter(
            quiz_attempt=quiz_attempt,
            question=question,
            choice=correct_choice
        ).exists()

    def test_complete_quiz(self, authenticated_client, quiz_attempt):
        """Test completing a quiz."""
        # Submit answers for all questions
        for question in quiz_attempt.quiz.question_set.all():
            correct_choice = question.choice_set.filter(is_correct=True).first()
            UserAnswer.objects.create(
                quiz_attempt=quiz_attempt,
                question=question,
                choice=correct_choice
            )
        
        response = authenticated_client.post(
            reverse('quiz:complete_quiz', kwargs={'attempt_id': quiz_attempt.pk})
        )
        assert response.status_code == 302
        assert 'results' in response['Location']
        
        quiz_attempt.refresh_from_db()
        assert quiz_attempt.completed_at is not None
        assert quiz_attempt.score == 100.0

    def test_quiz_results(self, authenticated_client, completed_quiz_attempt):
        """Test viewing quiz results."""
        response = authenticated_client.get(
            reverse('quiz:quiz_results', kwargs={'attempt_id': completed_quiz_attempt.pk})
        )
        assert response.status_code == 200
        assert str(completed_quiz_attempt.score) in str(response.content)

class TestQuizAdminViews:
    """Test cases for quiz administration views."""
    
    def test_create_quiz(self, admin_client):
        """Test creating a new quiz."""
        response = admin_client.post(
            reverse('quiz:create_quiz'),
            {
                'title': 'New Quiz',
                'description': 'Test Description',
                'passing_score': 80.0,
                'is_active': True
            }
        )
        assert response.status_code == 302
        assert 'New Quiz' in str(get_messages(response.wsgi_request))

    def test_edit_quiz(self, admin_client, quiz_with_questions):
        """Test editing an existing quiz."""
        new_title = 'Updated Quiz Title'
        response = admin_client.post(
            reverse('quiz:edit_quiz', kwargs={'pk': quiz_with_questions.pk}),
            {
                'title': new_title,
                'description': quiz_with_questions.description,
                'passing_score': quiz_with_questions.passing_score,
                'is_active': quiz_with_questions.is_active
            }
        )
        assert response.status_code == 302
        quiz_with_questions.refresh_from_db()
        assert quiz_with_questions.title == new_title

    def test_delete_quiz(self, admin_client, quiz_with_questions):
        """Test deleting a quiz."""
        response = admin_client.post(
            reverse('quiz:delete_quiz', kwargs={'pk': quiz_with_questions.pk})
        )
        assert response.status_code == 302
        assert 'successfully deleted' in str(get_messages(response.wsgi_request))
