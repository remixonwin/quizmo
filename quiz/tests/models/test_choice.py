"""
Tests for choice model functionality.
"""
from quiz.tests.base import QuizTestCase
from quiz.models import Choice

class ChoiceModelTests(QuizTestCase):
    """Test choice model."""

    def test_choice_without_question(self):
        """Test choice creation without question"""
        with self.assertRaises(ValueError):
            Choice.objects.create(text='Test Choice')

    def test_choice_order(self):
        """Test choice ordering"""
        # Choices are already created in setUpTestData
        question = self.quiz.questions.first()
        choices = Choice.objects.filter(question=question).order_by('order')
        for i, choice in enumerate(choices):
            self.assertEqual(choice.order, i)

    def test_multiple_correct_choices(self):
        """Test multiple correct choices validation"""
        question = self.quiz.questions.first()
        
        # First choice is already correct from setup
        # Try to create another correct choice
        with self.assertRaises(ValueError):
            Choice.objects.create(
                question=question,
                text='Another Correct Choice',
                is_correct=True
            )

    def test_choice_str_representation(self):
        """Test string representation of choice"""
        choice = Choice.objects.first()
        expected = f'{choice.question.text} - Choice {choice.order + 1}'
        self.assertEqual(str(choice), expected)
