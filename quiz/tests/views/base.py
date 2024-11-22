"""
Base test class for quiz views.
"""
from quiz.tests.base import QuizTestCase
from quiz.models import Quiz, Question, Choice, QuizAttempt

class BaseViewTest(QuizTestCase):
    """Base class for view tests with common setup and utility methods."""
    
    def create_quiz_attempt(self, correct_answers=None):
        """Create a quiz attempt with optional correct answers."""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.test_user
        )
        
        if correct_answers is not None:
            # Submit answers
            for i, question in enumerate(self.questions):
                is_correct = i < correct_answers
                choice = Choice.objects.get(
                    question=question,
                    is_correct=is_correct
                )
                attempt.answers.create(
                    question=question,
                    choice=choice
                )
        
        return attempt
