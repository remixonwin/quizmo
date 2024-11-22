"""
Choice factory for creating test choices.
"""
import factory
from quiz.models import Choice
from .question import QuestionFactory

class ChoiceFactory(factory.django.DjangoModelFactory):
    """Factory for creating test choices."""
    
    class Meta:
        model = Choice

    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker('sentence')
    explanation = factory.Faker('paragraph')
    order = factory.Sequence(lambda n: n)
    is_correct = False  # default to incorrect
    
    @classmethod
    def create_correct(cls, **kwargs):
        """Create a correct choice."""
        return cls.create(is_correct=True, **kwargs)
    
    @classmethod
    def create_incorrect(cls, **kwargs):
        """Create an incorrect choice."""
        return cls.create(is_correct=False, **kwargs)
