"""
Question factory for creating test questions.
"""
import factory
from quiz.models import Question
from .quiz import QuizFactory

class QuestionFactory(factory.django.DjangoModelFactory):
    """Factory for creating test questions."""
    
    class Meta:
        model = Question

    quiz = factory.SubFactory(QuizFactory)
    text = factory.Faker('sentence')
    explanation = factory.Faker('paragraph')
    order = factory.Sequence(lambda n: n)
    weight = factory.LazyFunction(lambda: 1.0)
    
    @factory.post_generation
    def with_choices(self, create, extracted, **kwargs):
        """Create choices for the question.
        
        Args:
            extracted: Number of choices to create. If not specified, creates 4.
            kwargs: Additional arguments for choice creation.
        """
        if not create:
            return
        
        if extracted:
            num_choices = extracted
        else:
            num_choices = 4  # default number of choices
            
        # Import here to avoid circular imports
        from .choice import ChoiceFactory
            
        # Create one correct choice
        ChoiceFactory(question=self, is_correct=True)
        
        # Create remaining incorrect choices
        ChoiceFactory.create_batch(num_choices - 1, question=self, is_correct=False)
