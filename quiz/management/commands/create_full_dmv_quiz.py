from django.core.management.base import BaseCommand
from quiz.models import Quiz, Question, Choice
import os
from django.core.files import File
from django.conf import settings
import random

class Command(BaseCommand):
    help = 'Creates a 40-question Minnesota DMV Practice Test with 25% image questions'

    def get_image(self, filename):
        image_path = os.path.join(settings.MEDIA_ROOT, 'question_images', filename)
        if os.path.exists(image_path):
            return File(open(image_path, 'rb'))
        return None

    def handle(self, *args, **kwargs):
        # Delete existing quiz if it exists
        Quiz.objects.filter(title="Minnesota DMV Practice Test").delete()

        # Create the quiz
        quiz = Quiz.objects.create(
            title="Minnesota DMV Practice Test",
            description="Official practice test with 40 questions (10 with traffic signs). You need 32 correct answers (80%) to pass."
        )

        # Traffic sign questions (our image pool)
        traffic_signs = [
            {
                'text': "What does this red octagonal sign mean?",
                'image_name': 'stop_sign.jpg',
                'choices': [
                    ('Stop completely and check for traffic', True),
                    ('Slow down and proceed with caution', False),
                    ('Stop only if other vehicles are present', False),
                    ('Yield to oncoming traffic', False)
                ]
            },
            {
                'text': "What does this sign mean?",
                'image_name': 'speed_70.jpg',
                'choices': [
                    ('Maximum speed limit is 70 mph', True),
                    ('Minimum speed limit is 70 mph', False),
                    ('Recommended speed is 70 mph', False),
                    ('Distance to next exit is 70 miles', False)
                ]
            },
            {
                'text': "What does this sign indicate?",
                'image_name': 'yield.jpg',
                'choices': [
                    ('Yield to oncoming traffic', True),
                    ('Stop completely', False),
                    ('Merge ahead', False),
                    ('School zone', False)
                ]
            },
            {
                'text': "What does this sign mean?",
                'image_name': 'do_not_enter.jpg',
                'choices': [
                    ('Do not enter this road', True),
                    ('Stop ahead', False),
                    ('Railroad crossing', False),
                    ('Construction zone', False)
                ]
            },
            {
                'text': "What does this sign indicate?",
                'image_name': 'merge.jpg',
                'choices': [
                    ('Traffic merging ahead', True),
                    ('Sharp turn ahead', False),
                    ('Lane ends', False),
                    ('Bridge ahead', False)
                ]
            },
            {
                'text': "What does this sign warn about?",
                'image_name': 'signal_ahead.jpg',
                'choices': [
                    ('Traffic signal ahead', True),
                    ('Railroad crossing', False),
                    ('School crossing', False),
                    ('Construction zone', False)
                ]
            },
            {
                'text': "What action should you take when you see this sign?",
                'image_name': 'curve_ahead.jpg',
                'choices': [
                    ('Slow down and prepare for a curve', True),
                    ('Stop completely', False),
                    ('Change lanes', False),
                    ('Increase speed', False)
                ]
            },
            {
                'text': "What hazard does this sign warn about?",
                'image_name': 'bump.jpg',
                'choices': [
                    ('Bump in the road ahead', True),
                    ('Slippery when wet', False),
                    ('Sharp curve ahead', False),
                    ('Bridge freezes before road', False)
                ]
            },
            {
                'text': "What should you watch for when you see this sign?",
                'image_name': 'bicycle_crossing.jpg',
                'choices': [
                    ('Bicycles crossing the road', True),
                    ('No bicycles allowed', False),
                    ('Bicycle parking area', False),
                    ('Bicycle lane ends', False)
                ]
            },
            {
                'text': "What is prohibited by this sign?",
                'image_name': 'no_left_turn.jpg',
                'choices': [
                    ('Left turns', True),
                    ('Right turns', False),
                    ('U-turns', False),
                    ('All turns', False)
                ]
            },
            {
                'text': "What does this sign indicate?",
                'image_name': 'railroad_crossing.jpg',
                'choices': [
                    ('Railroad crossing ahead', True),
                    ('Road work ahead', False),
                    ('School crossing', False),
                    ('Pedestrian crossing', False)
                ]
            },
            {
                'text': "What does this sign mean?",
                'image_name': 'no_u_turn.jpg',
                'choices': [
                    ('U-turns are prohibited', True),
                    ('No left turn', False),
                    ('No right turn', False),
                    ('Dead end ahead', False)
                ]
            },
            {
                'text': "What does this sign indicate?",
                'image_name': 'school_crossing.jpg',
                'choices': [
                    ('School crossing ahead', True),
                    ('Pedestrian crossing', False),
                    ('Railroad crossing', False),
                    ('Construction zone', False)
                ]
            },
            {
                'text': "What does this sign indicate?",
                'image_name': 'deer_crossing.jpg',
                'choices': [
                    ('Watch for deer crossing the road', True),
                    ('Wildlife sanctuary ahead', False),
                    ('Zoo ahead', False),
                    ('No hunting zone', False)
                ]
            },
            {
                'text': "What should you do when you see this sign?",
                'image_name': 'narrow_bridge.jpg',
                'choices': [
                    ('Slow down and be prepared for a narrow bridge', True),
                    ('Speed up to cross quickly', False),
                    ('Stop before the bridge', False),
                    ('Change lanes', False)
                ]
            },
            {
                'text': "What does this sign warn about?",
                'image_name': 'two_way_traffic.jpg',
                'choices': [
                    ('Two-way traffic ahead', True),
                    ('Divided highway begins', False),
                    ('Merge ahead', False),
                    ('Lane ends', False)
                ]
            },
            {
                'text': "What does this sign indicate?",
                'image_name': 'divided_highway_ends.jpg',
                'choices': [
                    ('Divided highway ends ahead', True),
                    ('Road ends ahead', False),
                    ('Bridge ahead', False),
                    ('Construction zone ahead', False)
                ]
            },
            {
                'text': "What does this sign mean?",
                'image_name': 'no_right_turn.jpg',
                'choices': [
                    ('Right turns are prohibited', True),
                    ('Right turn ahead', False),
                    ('Right turn yield', False),
                    ('One way to the right', False)
                ]
            },
            {
                'text': "What should you do when you see this sign?",
                'image_name': 'keep_right.jpg',
                'choices': [
                    ('Keep to the right of the sign', True),
                    ('Turn right at the next intersection', False),
                    ('Move to the right lane', False),
                    ('Pass on the right', False)
                ]
            },
            {
                'text': "What vehicles are prohibited by this sign?",
                'image_name': 'no_trucks.jpg',
                'choices': [
                    ('Trucks', True),
                    ('Cars', False),
                    ('Motorcycles', False),
                    ('Bicycles', False)
                ]
            },
            {
                'text': "What does this sign tell you?",
                'image_name': 'wrong_way.jpg',
                'choices': [
                    ('You are going the wrong way', True),
                    ('Road work ahead', False),
                    ('Detour ahead', False),
                    ('One way street', False)
                ]
            },
        ]

        # Non-image questions pool
        non_image_questions = [
            {
                'text': "What does this yellow diamond-shaped sign indicate?",
                'choices': [
                    ('Curve ahead', True),
                    ('Road ends', False),
                    ('Turn around', False),
                    ('Exit only', False)
                ]
            },
            {
                'text': "What does this sign mean?",
                'image_name': 'pedestrian_crossing.jpg',
                'choices': [
                    ('Pedestrian crossing ahead', True),
                    ('Playground ahead', False),
                    ('School zone', False),
                    ('Hospital zone', False)
                ]
            },
            {
                'text': "What action is required when you see this sign?",
                'image_name': 'one_way.jpg',
                'choices': [
                    ('Travel only in the direction of the arrow', True),
                    ('No left turns allowed', False),
                    ('Detour ahead', False),
                    ('Exit only', False)
                ]
            },
            {
                'text': "What is the speed limit in urban residential areas unless otherwise posted?",
                'choices': [
                    ('30 mph', True),
                    ('25 mph', False),
                    ('35 mph', False),
                    ('40 mph', False)
                ]
            },
            {
                'text': "When two vehicles reach an intersection without traffic signs or signals at the same time, who has the right of way?",
                'choices': [
                    ('The vehicle on the right', True),
                    ('The vehicle on the left', False),
                    ('The larger vehicle', False),
                    ('The faster vehicle', False)
                ]
            },
            {
                'text': "What is the legal blood alcohol concentration (BAC) limit for commercial drivers in Minnesota?",
                'choices': [
                    ('0.04%', True),
                    ('0.08%', False),
                    ('0.02%', False),
                    ('0.10%', False)
                ]
            },
            {
                'text': "How long must you signal before making a turn in traffic?",
                'choices': [
                    ('At least 100 feet', True),
                    ('At least 50 feet', False),
                    ('At least 200 feet', False),
                    ('At least 75 feet', False)
                ]
            },
            {
                'text': "When parking your vehicle on a hill with a curb and facing downhill, you should:",
                'choices': [
                    ('Turn your wheels toward the curb', True),
                    ('Turn your wheels away from the curb', False),
                    ('Keep your wheels straight', False),
                    ("It doesn't matter", False)
                ]
            },
            {
                'text': "What is the minimum age to obtain a Minnesota driver's license without restrictions?",
                'choices': [
                    ('18 years', True),
                    ('16 years', False),
                    ('17 years', False),
                    ('21 years', False)
                ]
            },
            {
                'text': "How many hours of behind-the-wheel driving instruction are required for a first-time driver's license applicant under 18?",
                'choices': [
                    ('6 hours', True),
                    ('8 hours', False),
                    ('4 hours', False),
                    ('10 hours', False)
                ]
            },
            {
                'text': "What is the fine for not wearing a seat belt in Minnesota?",
                'choices': [
                    ('$25', True),
                    ('$50', False),
                    ('$75', False),
                    ('$100', False)
                ]
            },
            {
                'text': "When can you drive in a bike lane?",
                'choices': [
                    ('Only when making a turn', True),
                    ('Never', False),
                    ('When no bicycles are present', False),
                    ('During rush hour', False)
                ]
            },
            {
                'text': "What is the speed limit in a school zone when children are present?",
                'choices': [
                    ('20 mph', True),
                    ('15 mph', False),
                    ('25 mph', False),
                    ('30 mph', False)
                ]
            },
            {
                'text': "What should you do if your vehicle starts to hydroplane?",
                'choices': [
                    ('Slowly take your foot off the gas', True),
                    ('Brake hard immediately', False),
                    ('Turn sharply to regain control', False),
                    ('Accelerate to power through', False)
                ]
            },
            {
                'text': "What is the proper technique for turning your steering wheel when making a turn?",
                'choices': [
                    ('Hand over hand', True),
                    ('One hand only', False),
                    ('Palm to palm', False),
                    ('Cross arms', False)
                ]
            },
            {
                'text': "When driving in fog, you should:",
                'choices': [
                    ('Use low beam headlights', True),
                    ('Use high beam headlights', False),
                    ('Use parking lights only', False),
                    ('Turn off all lights', False)
                ]
            },
            {
                'text': "What should you do if you have a tire blowout?",
                'choices': [
                    ('Grip the wheel firmly and slow down gradually', True),
                    ('Brake hard immediately', False),
                    ('Pull over immediately without slowing', False),
                    ('Speed up to maintain control', False)
                ]
            },
            {
                'text': "What is the recommended following distance in adverse weather conditions?",
                'choices': [
                    ('At least 6 seconds', True),
                    ('3 seconds', False),
                    ('2 seconds', False),
                    ('4 seconds', False)
                ]
            },
            {
                'text': "When should you check your vehicle's blind spots?",
                'choices': [
                    ('Before changing lanes or merging', True),
                    ('Only when changing lanes', False),
                    ('Only when merging', False),
                    ('Only in heavy traffic', False)
                ]
            },
            {
                'text': "What should you do when an emergency vehicle with sirens on approaches?",
                'choices': [
                    ('Pull over to the right and stop', True),
                    ('Speed up to get out of the way', False),
                    ('Stop immediately where you are', False),
                    ('Slow down but keep moving', False)
                ]
            },
            {
                'text': "What is the best way to begin driving in winter conditions?",
                'choices': [
                    ('Start slowly and test your traction', True),
                    ('Drive normally but more carefully', False),
                    ('Accelerate quickly to test conditions', False),
                    ('Brake hard to test traction', False)
                ]
            },
            {
                'text': "When driving through a work zone, you should:",
                'choices': [
                    ('Slow down and be prepared to stop', True),
                    ('Maintain your current speed', False),
                    ('Change lanes frequently', False),
                    ('Speed up to get through quickly', False)
                ]
            },
            {
                'text': "What should you do if your brakes fail?",
                'choices': [
                    ('Pump the brakes and use the emergency brake', True),
                    ('Turn off the engine immediately', False),
                    ('Swerve to the shoulder', False),
                    ('Coast to a stop', False)
                ]
            },
            {
                'text': "When driving in fog, you should use:",
                'choices': [
                    ('Low beam headlights', True),
                    ('High beam headlights', False),
                    ('Parking lights only', False),
                    ('Hazard lights while moving', False)
                ]
            },
            {
                'text': "What is the minimum following distance recommended in good weather conditions?",
                'choices': [
                    ('3 seconds', True),
                    ('1 second', False),
                    ('2 seconds', False),
                    ('5 seconds', False)
                ]
            },
            {
                'text': "When must you stop for a school bus?",
                'choices': [
                    ('When it displays flashing red lights and extends its stop arm', True),
                    ('Only when children are visible', False),
                    ('Only during school hours', False),
                    ('Only when in a school zone', False)
                ]
            },
            {
                'text': "What should you do if your brakes fail?",
                'choices': [
                    ('Pump the brake pedal and use the parking brake', True),
                    ('Turn off the engine immediately', False),
                    ('Swerve to the nearest soft shoulder', False),
                    ('Coast to a stop without steering', False)
                ]
            },
            {
                'text': "In Minnesota, what is the law regarding cell phone use while driving?",
                'choices': [
                    ('Only hands-free use is permitted', True),
                    ('No restrictions apply', False),
                    ('Complete ban on all cell phone use', False),
                    ('Only texting is prohibited', False)
                ]
            },
            {
                'text': "When merging onto a freeway, you should:",
                'choices': [
                    ('Accelerate to match the speed of traffic', True),
                    ('Always come to a complete stop first', False),
                    ('Maintain a steady speed of 45 mph', False),
                    ('Expect other drivers to move over', False)
                ]
            },
            {
                'text': "What is the proper action when approaching a roundabout?",
                'choices': [
                    ('Yield to vehicles already in the roundabout', True),
                    ('Speed up to merge quickly', False),
                    ('Stop completely before entering', False),
                    ('Maintain your current speed', False)
                ]
            },
            {
                'text': "When is it legal to pass on the right in Minnesota?",
                'choices': [
                    ('When the vehicle ahead is making a left turn', True),
                    ('Never', False),
                    ('Only on the highway', False),
                    ('When traffic is moving slowly', False)
                ]
            },
            {
                'text': "What is the speed limit in an alley?",
                'choices': [
                    ('10 mph', True),
                    ('15 mph', False),
                    ('20 mph', False),
                    ('25 mph', False)
                ]
            },
            {
                'text': "When driving through a work zone, you should:",
                'choices': [
                    ('Follow all special signs and reduce speed', True),
                    ('Maintain normal highway speeds', False),
                    ('Change lanes whenever possible', False),
                    ('Use hazard lights at all times', False)
                ]
            },
            {
                'text': "What is the first thing you should do if your vehicle starts to skid?",
                'choices': [
                    ('Take your foot off the accelerator', True),
                    ('Apply the brakes immediately', False),
                    ('Turn the steering wheel quickly', False),
                    ('Shift to neutral', False)
                ]
            },
            {
                'text': "When parking uphill with a curb, your wheels should be:",
                'choices': [
                    ('Turned away from the curb', True),
                    ('Turned towards the curb', False),
                    ('Parallel to the curb', False),
                    ('Position does not matter', False)
                ]
            }
        ]

        # Select questions
        image_questions = random.sample(traffic_signs, 10)  # 25% of 40 = 10 image questions
        non_image_selections = random.sample(non_image_questions, 30)  # Remaining 30 questions
        
        # Combine and shuffle all selected questions
        selected_questions = image_questions + non_image_selections
        random.shuffle(selected_questions)

        # Add questions to the quiz
        for q_data in selected_questions:
            question = Question(
                quiz=quiz,
                text=q_data['text']
            )
            
            if 'image_name' in q_data:
                image_file = self.get_image(q_data['image_name'])
                if image_file:
                    question.image.save(q_data['image_name'], image_file, save=True)
                    image_file.close()
                else:
                    question.save()
            else:
                question.save()
            
            for choice_text, is_correct in q_data['choices']:
                Choice.objects.create(
                    question=question,
                    text=choice_text,
                    is_correct=is_correct
                )

        self.stdout.write(self.style.SUCCESS('Successfully created DMV quiz with 40 questions (10 with images)'))
