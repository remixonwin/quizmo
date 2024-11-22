"""
Base test class for question tests.
"""
from quiz.models import Question, Choice
from .quiz import QuizTestCase
from .media import MediaTestCase

class QuestionTestCase(QuizTestCase, MediaTestCase):
    """Base test case for question tests."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test question data."""
        super().setUpTestData()
        
        # Create test questions with images
        cls.questions = []
        cls.correct_choices = []
        
        for i in range(5):
            # Use test images cyclically
            image_name = cls.test_images[i % len(cls.test_images)]
            
            question = Question.objects.create(
                quiz=cls.quiz,
                text=f'Test Question {i+1}',
                order=i,
                points=1,
                image=cls.get_image_path(image_name)
            )
            cls.questions.append(question)
            
            # Create choices for each question (1 correct, 3 incorrect)
            correct_choice = Choice.objects.create(
                question=question,
                text=f'Correct Answer {i+1}',
                is_correct=True,
                order=1
            )
            cls.correct_choices.append(correct_choice)
            
            # Create incorrect choices
            for j in range(3):
                Choice.objects.create(
                    question=question,
                    text=f'Wrong Answer {i+1}-{j+1}',
                    is_correct=False,
                    order=j+2
                )
    
    def create_question(self, quiz=None, **kwargs):
        """Create a test question.
        
        Args:
            quiz: Quiz to add question to. Defaults to self.quiz
            **kwargs: Additional fields for the question
        """
        quiz = quiz or self.quiz
        
        question = Question.objects.create(
            quiz=quiz,
            text=kwargs.get('text', 'Test Question'),
            order=kwargs.get('order', 0),
            points=kwargs.get('points', 1),
            image=kwargs.get('image', None)
        )
        
        # Create default choices if not specified
        if 'choices' not in kwargs:
            Choice.objects.create(
                question=question,
                text='Correct Answer',
                is_correct=True,
                order=1
            )
            
            for i in range(3):
                Choice.objects.create(
                    question=question,
                    text=f'Wrong Answer {i+1}',
                    is_correct=False,
                    order=i+2
                )
        else:
            for i, choice_data in enumerate(kwargs['choices']):
                Choice.objects.create(
                    question=question,
                    text=choice_data['text'],
                    is_correct=choice_data.get('is_correct', False),
                    order=choice_data.get('order', i+1)
                )
        
        return question
