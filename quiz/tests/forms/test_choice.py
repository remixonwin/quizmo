"""
Tests for choice form functionality.
"""
from django.test import TestCase
from quiz.forms import ChoiceForm
from quiz.models import Quiz, Question

class ChoiceFormTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test Description'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question'
        )

    def test_valid_choice_form(self):
        """Test choice form with valid data"""
        form_data = {
            'question': self.question.id,
            'text': 'Test Choice',
            'is_correct': True
        }
        form = ChoiceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_choice_form(self):
        """Test choice form with invalid data"""
        form_data = {
            'question': self.question.id,
            'text': '',  # Text is required
            'is_correct': True
        }
        form = ChoiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)

    def test_choice_form_without_question(self):
        """Test choice form without question"""
        form_data = {
            'text': 'Test Choice',
            'is_correct': True
        }
        form = ChoiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('question', form.errors)

    def test_choice_form_max_length(self):
        """Test choice form field max length"""
        form_data = {
            'question': self.question.id,
            'text': 'T' * 501,  # Max length is 500
            'is_correct': True
        }
        form = ChoiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
