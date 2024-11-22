"""
Tests for question model functionality.
"""
from quiz.tests.base import QuizTestCase
from quiz.models import Question

class QuestionModelTests(QuizTestCase):
    """Test question model."""

    def test_question_order(self):
        """Test question ordering"""
        # Questions are already created in setUpTestData
        # Verify they are in correct order
        questions = Question.objects.filter(quiz=self.quiz).order_by('order')
        for i, question in enumerate(questions):
            self.assertEqual(question.order, i)

    def test_question_str_representation(self):
        """Test string representation of question"""
        question = Question.objects.first()
        expected = f'{self.quiz.title} - Question {question.order + 1}'
        self.assertEqual(str(question), expected)

    def test_question_without_quiz(self):
        """Test question creation without quiz"""
        with self.assertRaises(ValueError):
            Question.objects.create(text='Test Question')

    def test_question_choice_count(self):
        """Test question choice count property"""
        question = Question.objects.first()
        self.assertEqual(question.choice_count, 4)  # From QuizTestCase setup
