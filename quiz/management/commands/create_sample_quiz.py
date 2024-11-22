from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz.models.quiz import Quiz, Question, Choice
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a sample Minnesota DMV Practice Quiz'

    def handle(self, *args, **kwargs):
        # Get or create admin user
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            self.stdout.write('Admin user not found')
            return

        # Create quiz
        quiz = Quiz.objects.create(
            title='Minnesota DMV Practice Test',
            description='Practice test for the Minnesota Driver\'s License exam. This quiz covers road signs, traffic laws, and safe driving practices.',
            created_by=admin_user,
            time_limit=30,
            pass_mark=75.00,
            success_text='Congratulations! You have passed the practice test.',
            fail_text='Keep practicing! Review the questions you missed and try again.',
            answers_at_end=True,
            random_order=True
        )

        # Create questions and choices
        questions_data = [
            {
                'text': 'What does a red octagonal sign mean?',
                'explanation': 'A red octagonal sign always means STOP. You must come to a complete stop at the stop line.',
                'choices': [
                    ('Stop completely', True),
                    ('Slow down', False),
                    ('Yield to traffic', False),
                    ('Proceed with caution', False),
                ]
            },
            {
                'text': 'What is the speed limit in a residential area unless otherwise posted?',
                'explanation': 'In Minnesota, the default speed limit in residential areas is 30 mph unless otherwise posted.',
                'choices': [
                    ('20 mph', False),
                    ('25 mph', False),
                    ('30 mph', True),
                    ('35 mph', False),
                ]
            },
            {
                'text': 'When must you use your headlights?',
                'explanation': 'Minnesota law requires headlight use from sunset to sunrise and during adverse weather conditions.',
                'choices': [
                    ('Only at night', False),
                    ('From sunset to sunrise and during adverse weather', True),
                    ('When you think you need them', False),
                    ('Only during rain', False),
                ]
            },
            {
                'text': 'What is the minimum following distance recommended for normal driving conditions?',
                'explanation': 'The three-second rule is recommended for normal driving conditions. In adverse conditions, increase this distance.',
                'choices': [
                    ('1 second', False),
                    ('2 seconds', False),
                    ('3 seconds', True),
                    ('4 seconds', False),
                ]
            },
            {
                'text': 'What should you do if your vehicle starts to hydroplane?',
                'explanation': 'When hydroplaning, gradually ease off the accelerator and hold the steering wheel straight until you regain control.',
                'choices': [
                    ('Brake hard immediately', False),
                    ('Turn the steering wheel quickly', False),
                    ('Accelerate to power through', False),
                    ('Ease off the accelerator and keep steering straight', True),
                ]
            }
        ]

        for i, q_data in enumerate(questions_data):
            question = Question.objects.create(
                quiz=quiz,
                text=q_data['text'],
                explanation=q_data['explanation'],
                order=i
            )
            
            for j, (choice_text, is_correct) in enumerate(q_data['choices']):
                Choice.objects.create(
                    question=question,
                    text=choice_text,
                    is_correct=is_correct,
                    order=j
                )

        self.stdout.write(self.style.SUCCESS('Successfully created sample quiz'))
