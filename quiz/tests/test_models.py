from django.test import TestCase
from quiz.models import Quiz, Question, Choice
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class QuizModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            description="A test quiz description"
        )

    def test_quiz_creation(self):
        """Test quiz creation with valid data"""
        self.assertEqual(self.quiz.title, "Test Quiz")
        self.assertEqual(self.quiz.description, "A test quiz description")
        self.assertTrue(self.quiz.created_at)

    def test_quiz_str_representation(self):
        """Test string representation of Quiz model"""
        self.assertEqual(str(self.quiz), "Test Quiz")

    def test_quiz_calculate_score(self):
        """Test quiz score calculation"""
        # Create questions with choices
        for i in range(40):
            question = Question.objects.create(
                quiz=self.quiz,
                text=f"Question {i+1}"
            )
            # Create 4 choices per question, one correct
            for j in range(4):
                Choice.objects.create(
                    question=question,
                    text=f"Choice {j+1}",
                    is_correct=(j == 0)  # First choice is correct
                )

        score_data = self.quiz.calculate_score()
        self.assertEqual(score_data['total_questions'], 40)
        self.assertEqual(score_data['required_to_pass'], 32)
        self.assertEqual(score_data['correct_answers'], 40)
        self.assertEqual(score_data['score'], 100)
        self.assertTrue(score_data['passed'])

    def test_quiz_with_no_questions(self):
        """Test quiz score calculation with no questions"""
        score_data = self.quiz.calculate_score()
        self.assertEqual(score_data['score'], 0)
        self.assertFalse(score_data['passed'])

class QuestionModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            description="Test Description"
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="Test Question"
        )

    def test_question_creation(self):
        """Test question creation with valid data"""
        self.assertEqual(self.question.text, "Test Question")
        self.assertEqual(self.question.quiz, self.quiz)
        self.assertTrue(self.question.created_at)

    def test_question_str_representation(self):
        """Test string representation of Question model"""
        self.assertEqual(str(self.question), "Test Question")

    def test_question_without_quiz(self):
        """Test question creation without quiz"""
        with self.assertRaises(IntegrityError):
            Question.objects.create(text="Invalid Question")

class ChoiceModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            description="Test Description"
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="Test Question"
        )
        self.choice = Choice.objects.create(
            question=self.question,
            text="Test Choice",
            is_correct=True
        )

    def test_choice_creation(self):
        """Test choice creation with valid data"""
        self.assertEqual(self.choice.text, "Test Choice")
        self.assertEqual(self.choice.question, self.question)
        self.assertTrue(self.choice.is_correct)

    def test_choice_str_representation(self):
        """Test string representation of Choice model"""
        self.assertEqual(str(self.choice), "Test Choice")

    def test_multiple_correct_choices(self):
        """Test multiple correct choices for one question"""
        # Create another correct choice
        second_choice = Choice.objects.create(
            question=self.question,
            text="Second Choice",
            is_correct=True
        )
        self.assertTrue(second_choice.is_correct)
        # Verify both choices exist and are correct
        correct_choices = Choice.objects.filter(
            question=self.question,
            is_correct=True
        )
        self.assertEqual(correct_choices.count(), 2)

    def test_choice_without_question(self):
        """Test choice creation without question"""
        with self.assertRaises(IntegrityError):
            Choice.objects.create(
                text="Invalid Choice",
                is_correct=True
            )
