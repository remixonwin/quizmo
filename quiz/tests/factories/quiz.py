"""
Quiz factory for creating test quizzes.
"""
import factory
from django.utils import timezone
from quiz.models import Quiz
from .user import UserFactory

class QuizFactory(factory.django.DjangoModelFactory):
    """Factory for creating test quizzes."""
    
    class Meta:
        model = Quiz

    title = factory.Sequence(lambda n: f'Quiz {n}')
    description = factory.Faker('text', max_nb_chars=200)
    is_active = True
    passing_score = factory.LazyFunction(lambda: 80.0)
    created_at = factory.LazyFunction(lambda: timezone.now())
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def with_questions(self, create, extracted, **kwargs):
        """Create questions for the quiz.
        
        Args:
            extracted: Number of questions to create. If not specified, creates 3.
            kwargs: Additional arguments for question creation.
        """
        if not create:
            return
        
        if extracted:
            num_questions = extracted
        else:
            num_questions = 3  # default number of questions
            
        # Import here to avoid circular imports
        from .question import QuestionFactory
        from .choice import ChoiceFactory
            
        for _ in range(num_questions):
            question = QuestionFactory(quiz=self)
            ChoiceFactory(question=question, is_correct=True)
            ChoiceFactory.create_batch(3, question=question, is_correct=False)
            
    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to the quiz if specified."""
        if not create:
            return

        if extracted:
            self.tags = extracted
