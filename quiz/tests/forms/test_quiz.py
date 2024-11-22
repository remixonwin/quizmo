"""
Tests for quiz form functionality.
"""
from django.test import TestCase
from quiz.forms import QuizForm

class QuizFormTests(TestCase):
    def test_valid_quiz_form(self):
        """Test quiz form with valid data"""
        form_data = {
            'title': 'Test Quiz',
            'description': 'Test Description'
        }
        form = QuizForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_quiz_form(self):
        """Test quiz form with invalid data"""
        form_data = {
            'title': '',  # Title is required
            'description': 'Test Description'
        }
        form = QuizForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_quiz_form_max_length(self):
        """Test quiz form field max lengths"""
        form_data = {
            'title': 'T' * 201,  # Max length is 200
            'description': 'D' * 1001  # Max length is 1000
        }
        form = QuizForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('description', form.errors)
