import factory
from django.contrib.auth.models import User
from quiz.models import Quiz, Question, Choice
from django.utils import timezone

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    title = factory.Sequence(lambda n: f'Quiz {n}')
    description = factory.Faker('text', max_nb_chars=200)
    is_active = True
    passing_score = factory.LazyFunction(lambda: 80.0)
    created_at = factory.LazyFunction(lambda: timezone.now())

    @factory.post_generation
    def with_questions(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            num_questions = extracted
        else:
            num_questions = 3  # default number of questions
            
        for _ in range(num_questions):
            question = QuestionFactory(quiz=self)
            ChoiceFactory(question=question, is_correct=True)
            ChoiceFactory.create_batch(3, question=question, is_correct=False)

class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    quiz = factory.SubFactory(QuizFactory)
    text = factory.Faker('sentence')
    explanation = factory.Faker('paragraph')
    order = factory.Sequence(lambda n: n)

class ChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Choice

    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker('sentence')
    is_correct = factory.Faker('boolean')
    explanation = factory.Faker('paragraph')
    order = factory.Sequence(lambda n: n)
