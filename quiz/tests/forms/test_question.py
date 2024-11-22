"""
Tests for question form functionality.
"""
from django.test import TestCase
from quiz.forms import QuestionForm
from quiz.models import Quiz

class QuestionFormTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description'
        )

    def test_valid_question_form(self):
        """Test question form with valid data"""
        form_data = {
            'quiz': self.quiz.id,
            'text': 'Test Question',
            'image': None
        }
        form = QuestionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_question_form(self):
        """Test question form with invalid data"""
        form_data = {
            'quiz': self.quiz.id,
            'text': '',  # Text is required
            'image': None
        }
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)

    def test_question_form_without_quiz(self):
        """Test question form without quiz"""
        form_data = {
            'text': 'Test Question',
            'image': None
        }
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quiz', form.errors)

    def test_question_form_max_length(self):
        """Test question form field max length"""
        form_data = {
            'quiz': self.quiz.id,
            'text': 'T' * 1001,  # Max length is 1000
            'image': None
        }
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
