from django.core.management.base import BaseCommand
from quiz.models import Quiz, Question, Choice
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates sample quizzes for testing'

    def handle(self, *args, **kwargs):
        # Create Quiz 1: Road Signs
        road_signs_quiz = Quiz.objects.create(
            title="Road Signs Practice Test",
            description="Test your knowledge of common road signs and traffic signals. This practice test covers regulatory signs, warning signs, and guide signs.",
            is_active=True,
            created_at=timezone.now()
        )

        # Questions for Road Signs Quiz
        questions_signs = [
            {
                "text": "What does a red octagonal sign mean?",
                "choices": [
                    ("Stop completely", True),
                    ("Slow down", False),
                    ("Yield to traffic", False),
                    ("Merge ahead", False)
                ]
            },
            {
                "text": "What does a yellow diamond-shaped sign indicate?",
                "choices": [
                    ("Construction zone", False),
                    ("Warning or hazard ahead", True),
                    ("School zone", False),
                    ("Speed limit", False)
                ]
            },
            {
                "text": "What does a round sign with a red circle and slash mean?",
                "choices": [
                    ("No entry or prohibited action", True),
                    ("Railroad crossing", False),
                    ("One way street", False),
                    ("Construction ahead", False)
                ]
            }
        ]

        # Create Quiz 2: Traffic Rules
        traffic_rules_quiz = Quiz.objects.create(
            title="Traffic Rules and Regulations",
            description="Practice questions about Minnesota traffic laws, right-of-way rules, speed limits, and safe driving practices.",
            is_active=True,
            created_at=timezone.now()
        )

        # Questions for Traffic Rules Quiz
        questions_rules = [
            {
                "text": "What is the speed limit in a residential area unless otherwise posted?",
                "choices": [
                    ("30 mph", True),
                    ("25 mph", False),
                    ("35 mph", False),
                    ("40 mph", False)
                ]
            },
            {
                "text": "When must you yield to a pedestrian?",
                "choices": [
                    ("Only at marked crosswalks", False),
                    ("Only when traffic signals indicate", False),
                    ("At all intersections, whether marked or unmarked", True),
                    ("Only in school zones", False)
                ]
            },
            {
                "text": "What is the minimum safe following distance in good weather conditions?",
                "choices": [
                    ("2 seconds", False),
                    ("3 seconds", True),
                    ("4 seconds", False),
                    ("5 seconds", False)
                ]
            }
        ]

        # Create questions and choices for both quizzes
        for quiz, questions in [(road_signs_quiz, questions_signs), (traffic_rules_quiz, questions_rules)]:
            for q_data in questions:
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data["text"]
                )
                for choice_text, is_correct in q_data["choices"]:
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=is_correct
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created sample quizzes'))
