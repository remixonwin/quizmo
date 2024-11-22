from django.core.management.base import BaseCommand
from quiz.models import Quiz, Question, Choice
import random

class Command(BaseCommand):
    help = 'Populates the database with 40 road sign questions'

    def handle(self, *args, **options):
        # Get or create the Minnesota DMV quiz
        quiz = Quiz.objects.get_or_create(
            title="Minnesota Road Signs Practice Test",
            defaults={
                'description': "Practice test for Minnesota road signs. You need to answer 32 out of 40 questions correctly to pass.",
                'time_limit': 60,  # 60 minutes
                'is_active': True,
            }
        )[0]

        # Clear existing questions for this quiz
        Question.objects.filter(quiz=quiz).delete()

        # List of road signs and their descriptions
        road_signs = [
            {
                'question': "What does this STOP sign indicate?",
                'explanation': "A STOP sign requires drivers to make a complete stop at the designated stopping point.",
                'choices': [
                    ('Come to a complete stop', True),
                    ('Slow down only', False),
                    ('Yield to other traffic', False),
                    ('Stop if other cars are present', False),
                ]
            },
            {
                'question': "What does this YIELD sign mean?",
                'explanation': "A YIELD sign requires drivers to slow down and give the right-of-way to other traffic.",
                'choices': [
                    ('Give right-of-way to other traffic', True),
                    ('Come to a complete stop', False),
                    ('Proceed without slowing', False),
                    ('Stop only for pedestrians', False),
                ]
            },
            {
                'question': "What does this School Zone sign indicate?",
                'explanation': "A School Zone sign warns drivers to slow down and watch for children in the area.",
                'choices': [
                    ('School zone ahead, watch for children', True),
                    ('Playground area', False),
                    ('Residential area', False),
                    ('Construction zone', False),
                ]
            },
            {
                'question': "What does this Railroad Crossing sign mean?",
                'explanation': "A Railroad Crossing sign warns drivers of an upcoming railroad crossing.",
                'choices': [
                    ('Railroad crossing ahead', True),
                    ('Intersection ahead', False),
                    ('Bridge ahead', False),
                    ('Construction zone', False),
                ]
            },
            {
                'question': "What does this Merge sign indicate?",
                'explanation': "A Merge sign warns drivers that traffic lanes are merging.",
                'choices': [
                    ('Traffic lanes are merging', True),
                    ('Road divides ahead', False),
                    ('Two-way traffic ahead', False),
                    ('Lane ends, move over', False),
                ]
            },
            {
                'question': "What does this Speed Limit sign mean?",
                'explanation': "A Speed Limit sign indicates the maximum legal speed limit under ideal conditions.",
                'choices': [
                    ('Maximum legal speed limit', True),
                    ('Minimum speed required', False),
                    ('Advisory speed limit', False),
                    ('School zone speed limit', False),
                ]
            },
            {
                'question': "What does this One Way sign indicate?",
                'explanation': "A One Way sign indicates that traffic is allowed to move only in the direction of the arrow.",
                'choices': [
                    ('Traffic moves only in one direction', True),
                    ('Two-way traffic ahead', False),
                    ('Turn allowed in direction of arrow', False),
                    ('Dead end ahead', False),
                ]
            },
            {
                'question': "What does this Do Not Enter sign mean?",
                'explanation': "A Do Not Enter sign prohibits entry into a roadway or area where traffic is moving in the opposite direction.",
                'choices': [
                    ('Entry is prohibited', True),
                    ('Stop ahead', False),
                    ('Wrong way', False),
                    ('Road closed', False),
                ]
            },
            {
                'question': "What does this Pedestrian Crossing sign indicate?",
                'explanation': "A Pedestrian Crossing sign warns drivers to watch for people crossing the street.",
                'choices': [
                    ('Watch for pedestrians crossing', True),
                    ('School zone ahead', False),
                    ('Playground area', False),
                    ('Bicycle crossing', False),
                ]
            },
            {
                'question': "What does this Curve Ahead sign mean?",
                'explanation': "A Curve Ahead sign warns drivers of an upcoming curve in the road.",
                'choices': [
                    ('Road curves ahead', True),
                    ('Winding road ahead', False),
                    ('Turn prohibited', False),
                    ('Slippery when wet', False),
                ]
            }
        ]

        # Multiply the questions to get 40
        extended_signs = road_signs * 4

        # Create 40 questions
        for i, sign in enumerate(extended_signs, 1):
            # Create question
            question = Question.objects.create(
                quiz=quiz,
                text=f"{sign['question']} (Question {i})",
                explanation=sign['explanation'],
                order=i,
                is_active=True,
                difficulty='medium',
                points=1.0
            )

            # Create choices for the question
            for text, is_correct in sign['choices']:
                Choice.objects.create(
                    question=question,
                    text=text,
                    is_correct=is_correct,
                    is_active=True
                )

        self.stdout.write(self.style.SUCCESS('Successfully created 40 questions'))
