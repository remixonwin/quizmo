"""
Tests for question bank functionality.
"""
import uuid
import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.utils import IntegrityError
from ..models.question_bank import QuestionBank, BankQuestion, BankChoice
from ..models.quiz import Quiz

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def bank(db, user):
    """Create a test question bank."""
    return QuestionBank.objects.create(
        name=f'Test Bank {uuid.uuid4()}',
        description='Test bank description',
        owner=user,
        tags=['test']
    )


@pytest.fixture
def bank_question(bank):
    """Create a test bank question."""
    return BankQuestion.objects.create(
        text='Test question',
        explanation='Test explanation',
        bank=bank,
        order=1
    )


@pytest.fixture
def bank_choices(bank_question):
    """Create test choices for the bank question."""
    choices = []
    for i, is_correct in enumerate([True, False, False]):
        choice = BankChoice.objects.create(
            text=f'Choice {i + 1}',
            question=bank_question,
            is_correct=is_correct
        )
        choices.append(choice)
    return choices


@pytest.fixture
def quiz(user, bank):
    """Create a test quiz using the bank."""
    return Quiz.objects.create(
        title='Test Quiz',
        description='Test quiz description',
        owner=user,
        bank=bank,
        passing_score=70.0
    )


@pytest.mark.django_db
class TestQuestionBank:
    """Test question bank model."""

    def test_create_bank(self):
        """Test creating a question bank."""
        bank = QuestionBank.objects.create(
            name=f'Test Bank {uuid.uuid4()}',
            description='Test description',
            owner=User.objects.first(),
            tags=['test']
        )
        assert bank.name.startswith('Test Bank')
        assert bank.description == 'Test description'
        assert bank.is_active is True

    def test_unique_name(self, bank):
        """Test that bank names must be unique."""
        with pytest.raises(IntegrityError):
            QuestionBank.objects.create(
                name=bank.name,
                description='Another description',
                owner=User.objects.first(),
                tags=['test']
            )

    def test_str_representation(self, bank):
        """Test string representation."""
        assert str(bank).startswith('Test Bank')

    def test_get_questions_cached(self, bank, bank_question):
        """Test getting questions with caching."""
        # Clear cache
        cache.clear()

        # First call should hit database
        questions = bank.get_questions()
        assert len(questions) == 1
        assert questions[0] == bank_question

        # Second call should hit cache
        cache_key = bank.get_cache_key(f'bank_questions_{bank.id}')
        assert cache.get(cache_key) == questions

    def test_get_questions_inactive(self, bank, bank_question):
        """Test that inactive questions are excluded."""
        bank_question.is_active = False
        bank_question.save()
        
        questions = bank.get_questions()
        assert len(questions) == 0

    def test_get_questions_limit(self, bank):
        """Test question limit."""
        # Create multiple questions
        for i in range(5):
            BankQuestion.objects.create(
                text=f'Question {i}',
                bank=bank,
                order=i
            )
        
        # Get limited questions
        questions = bank.get_questions(limit=3)
        assert len(questions) == 3
        assert questions[0].text == 'Question 0'
        assert questions[2].text == 'Question 2'

    def test_question_ordering(self, bank):
        """Test question ordering."""
        q2 = BankQuestion.objects.create(
            text='Question 2',
            bank=bank,
            order=2
        )
        q1 = BankQuestion.objects.create(
            text='Question 1',
            bank=bank,
            order=1
        )
        
        questions = bank.get_questions()
        assert questions[0] == q1
        assert questions[1] == q2

    def test_cache_invalidation(self, bank, bank_question):
        """Test cache invalidation on save."""
        # Clear cache
        cache.clear()

        # First call should hit database
        questions1 = bank.get_questions()
        
        # Create a new question (shouldn't affect cached questions)
        BankQuestion.objects.create(
            text='Another question',
            bank=bank,
            order=2
        )
        
        # Second call should return cached questions
        questions2 = bank.get_questions()
        assert len(questions2) == len(questions1)

        # Save bank to invalidate cache
        bank.save()
        
        # Third call should return updated questions
        questions3 = bank.get_questions()
        assert len(questions3) == 2


@pytest.mark.django_db
class TestBankQuestion:
    """Test bank question model."""

    def test_create_question(self, bank):
        """Test creating a bank question."""
        question = BankQuestion.objects.create(
            text='Test question',
            explanation='Test explanation',
            bank=bank,
            order=1
        )
        assert question.text == 'Test question'
        assert question.explanation == 'Test explanation'
        assert question.bank == bank
        assert question.order == 1
        assert question.is_active is True

    def test_str_representation(self, bank_question):
        """Test string representation."""
        assert str(bank_question) == 'Test question'

    def test_get_choices(self, bank_question, bank_choices):
        """Test getting choices with caching."""
        # Clear cache
        cache.clear()

        # First call should hit database
        choices = bank_question.get_choices()
        assert len(choices) == 3
        assert choices[0].is_correct is True
        assert choices[1].is_correct is False
        assert choices[2].is_correct is False

        # Second call should hit cache
        cache_key = bank_question.get_cache_key(f'question_choices_{bank_question.id}')
        assert cache.get(cache_key) == choices


@pytest.mark.django_db
class TestBankChoice:
    """Test bank choice model."""

    def test_create_choice(self, bank_question):
        """Test creating a bank choice."""
        choice = BankChoice.objects.create(
            text='Test choice',
            question=bank_question,
            is_correct=True,
            explanation='Test explanation'
        )
        assert choice.text == 'Test choice'
        assert choice.question == bank_question
        assert choice.is_correct is True
        assert choice.explanation == 'Test explanation'

    def test_str_representation(self, bank_choices):
        """Test string representation."""
        assert str(bank_choices[0]) == 'Choice 1'
