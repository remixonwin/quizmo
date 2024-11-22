"""
Tests for basic quiz scoring functionality.
"""
import json
from django.urls import reverse
from django.utils import timezone
from quiz.tests.scoring.base import BaseScoringTest

class BasicScoringTests(BaseScoringTest):
    """Test basic quiz scoring functionality."""

    def test_perfect_score(self):
        """Test scoring when all answers are correct"""
        # Submit all correct answers
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
        
        # Check redirect to results
        self.assertEqual(response.status_code, 302)
        
        # Verify attempt score
        attempt = self.attempt.__class__.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.score, 100.0)
        self.assertEqual(attempt.metadata['correct_answers'], 3)
        self.assertEqual(attempt.metadata['earned_points'], 6.0)
        
        # Verify difficulty stats
        diff_stats = attempt.metadata['difficulty_stats']
        self.assertEqual(diff_stats['easy']['correct'], 1)
        self.assertEqual(diff_stats['medium']['correct'], 1)
        self.assertEqual(diff_stats['hard']['correct'], 1)

    def test_partial_score(self):
        """Test scoring when some answers are incorrect"""
        # Submit mixed answers (correct easy, wrong medium, correct hard)
        answers = []
        for q in self.questions:
            if q.difficulty == 'medium':
                choice = q.choices.filter(is_correct=False).first()
            else:
                choice = q.choices.filter(is_correct=True).first()
            answers.append({
                'question_id': q.id,
                'choice_id': choice.id
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
        
        # Check redirect to results
        self.assertEqual(response.status_code, 302)
        
        # Verify attempt score
        attempt = self.attempt.__class__.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.score, 66.67)  # (4 points out of 6)
        self.assertEqual(attempt.metadata['correct_answers'], 2)
        self.assertEqual(attempt.metadata['earned_points'], 4.0)
        
        # Verify difficulty stats
        diff_stats = attempt.metadata['difficulty_stats']
        self.assertEqual(diff_stats['easy']['correct'], 1)
        self.assertEqual(diff_stats['medium']['correct'], 0)
        self.assertEqual(diff_stats['hard']['correct'], 1)

    def test_zero_score(self):
        """Test scoring when all answers are incorrect"""
        # Submit all wrong answers
        answers = []
        for q in self.questions:
            wrong_choice = q.choices.filter(is_correct=False).first()
            answers.append({
                'question_id': q.id,
                'choice_id': wrong_choice.id
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
        
        # Check redirect to results
        self.assertEqual(response.status_code, 302)
        
        # Verify attempt score
        attempt = self.attempt.__class__.objects.get(id=self.attempt.id)
        self.assertEqual(attempt.score, 0.0)
        self.assertEqual(attempt.metadata['correct_answers'], 0)
        self.assertEqual(attempt.metadata['earned_points'], 0.0)
        
        # Verify difficulty stats
        diff_stats = attempt.metadata['difficulty_stats']
        self.assertEqual(diff_stats['easy']['correct'], 0)
        self.assertEqual(diff_stats['medium']['correct'], 0)
        self.assertEqual(diff_stats['hard']['correct'], 0)
