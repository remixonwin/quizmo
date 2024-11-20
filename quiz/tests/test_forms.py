from django.test import TestCase
from quiz.forms import QuizForm, QuestionForm, ChoiceForm
from quiz.models import Quiz, Question, Choice

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
        }
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)

    def test_question_form_without_quiz(self):
        """Test question form without quiz"""
        form_data = {
            'text': 'Test Question',
        }
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quiz', form.errors)

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
            'text': 'T' * 201,  # Max length is 200
            'is_correct': True
        }
        form = ChoiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
