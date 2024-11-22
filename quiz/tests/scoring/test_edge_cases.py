"""
Tests for edge cases in quiz scoring.
"""
import json
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from quiz.tests.scoring.base import BaseScoringTest
from quiz.models import Question, Choice

class EdgeCaseTests(BaseScoringTest):
    """Test edge cases in quiz scoring."""

    def test_retake_quiz(self):
        """Test scoring when retaking a quiz"""
        # Complete first attempt with all wrong answers
        answers = []
        for q in self.questions:
            wrong_choice = q.choices.filter(is_correct=False).first()
            answers.append({
                'question_id': q.id,
                'choice_id': wrong_choice.id
            })
            
        self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json'
        )
        
        # Start new attempt
        response = self.client.post(
            reverse('quiz:start_quiz', args=[self.quiz.id]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Submit second attempt with all correct answers
        answers = []
        for q in self.questions:
            correct_choice = q.choices.filter(is_correct=True).first()
            answers.append({
                'question_id': q.id,
                'choice_id': correct_choice.id
            })
            
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json'
        )
        
        # Verify both attempts exist with correct scores
        attempts = self.attempt.__class__.objects.filter(
            quiz=self.quiz,
            user=self.user
        ).order_by('started_at')
        
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0].score, 0.0)
        self.assertEqual(attempts[1].score, 100.0)

    def test_question_weight_changes(self):
        """Test scoring when question weights change mid-attempt"""
        # Start attempt
        cache_key = f'attempt_{self.user.id}_{self.quiz.id}'
        
        # Change question weights
        for q in self.questions:
            q.points *= 2  # Double all points
            q.save()
            
        # Submit answers
        answers = []
        for q in self.questions:
            correct_choice = q.choices.filter(is_correct=True).first()
            answers.append({
                'question_id': q.id,
                'choice_id': correct_choice.id
            })
            
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json'
        )
        
        # Verify original weights were used
        attempt = self.attempt.__class__.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.metadata['earned_points'], 6.0)  # Original points
        
    def test_deleted_question(self):
        """Test scoring when a question is deleted during attempt"""
        # Delete a question mid-attempt
        deleted_q = self.questions[1]  # Medium question
        deleted_q_id = deleted_q.id
        deleted_q.delete()
        
        # Submit answers for remaining questions
        answers = []
        for q in [self.questions[0], self.questions[2]]:  # Skip deleted question
            correct_choice = q.choices.filter(is_correct=True).first()
            answers.append({
                'question_id': q.id,
                'choice_id': correct_choice.id
            })
            
        response = self.client.post(
            reverse('quiz:quiz_submit', args=[self.quiz.id]),
            data=json.dumps({
                'answers': answers,
                'metadata': {
                    'submittedAt': timezone.now().isoformat(),
                    'timeZone': 'UTC',
                    'userAgent': 'Mozilla/5.0 (Test)'
                }
            }),
            content_type='application/json'
        )
        
        # Verify score calculation excludes deleted question
        attempt = self.attempt.__class__.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.metadata['earned_points'], 4.0)  # 1 + 3 points
        self.assertEqual(attempt.score, 100.0)  # All answered correctly
