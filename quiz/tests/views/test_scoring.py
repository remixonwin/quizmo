"""
Tests for quiz scoring views.
"""
from django.urls import reverse
from django.utils import timezone
from quiz.tests.views.base import BaseViewTest
from quiz.models import QuizAttempt

class QuizScoringViewTests(BaseViewTest):
    """Test cases for quiz scoring views."""

    def test_submit_quiz_success(self):
        """Test successful quiz submission."""
        # Create an active attempt
        attempt = self.create_quiz_attempt()
        
        # Submit all correct answers
        answers = []
        for question in self.questions:
            correct_choice = question.choices.filter(is_correct=True).first()
            answers.append({
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
        
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data={
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            },
            content_type='application/json'
        )
        
        # Check redirect to results
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, 
                           reverse('quiz:quiz_results', args=[self.quiz.id]))
        
        # Verify attempt completion
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)
        self.assertEqual(attempt.score, 100.0)

    def test_view_quiz_results(self):
        """Test viewing quiz results."""
        # Create completed attempt with some correct answers
        attempt = self.create_quiz_attempt(correct_answers=2)
        attempt.completed_at = timezone.now()
        attempt.score = 66.67  # 2/3 correct
        attempt.save()
        
        response = self.client.get(
            reverse('quiz:quiz_results', args=[self.quiz.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/results.html')
        
        # Verify context data
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(response.context['attempt'], attempt)
        self.assertEqual(response.context['score'], 66.67)
        
    def test_view_quiz_history(self):
        """Test viewing quiz attempt history."""
        # Create multiple attempts
        attempt1 = self.create_quiz_attempt(correct_answers=1)
        attempt1.completed_at = timezone.now()
        attempt1.score = 33.33
        attempt1.save()
        
        attempt2 = self.create_quiz_attempt(correct_answers=2)
        attempt2.completed_at = timezone.now()
        attempt2.score = 66.67
        attempt2.save()
        
        response = self.client.get(
            reverse('quiz:quiz_history', args=[self.quiz.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/history.html')
        
        # Verify attempts are listed in reverse chronological order
        attempts = response.context['attempts']
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0], attempt2)
        self.assertEqual(attempts[1], attempt1)

    def test_resume_incomplete_quiz(self):
        """Test resuming an incomplete quiz attempt."""
        # Create incomplete attempt
        attempt = self.create_quiz_attempt()
        
        response = self.client.get(
            reverse('quiz:quiz_take', args=[self.quiz.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/take.html')
        
        # Verify attempt is resumed
        self.assertEqual(response.context['attempt'], attempt)
        self.assertFalse(response.context['is_completed'])

    def test_start_new_quiz(self):
        """Test starting a new quiz attempt."""
        response = self.client.post(
            reverse('quiz:start_quiz', args=[self.quiz.id]),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify new attempt was created
        attempt_id = data.get('attempt_id')
        self.assertIsNotNone(attempt_id)
        
        attempt = QuizAttempt.objects.get(id=attempt_id)
        self.assertEqual(attempt.quiz, self.quiz)
        self.assertEqual(attempt.user, self.test_user)
        self.assertIsNone(attempt.completed_at)
