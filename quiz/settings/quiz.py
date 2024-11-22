"""
Quiz-specific settings.
"""

# Quiz-specific URLs
MN_DRIVERS_MANUAL_URL = 'https://dps.mn.gov/divisions/dvs/forms-documents/Documents/Minnesota_Drivers_Manual.pdf'
MN_DVS_PRACTICE_TEST_URL = 'https://dps.mn.gov/divisions/dvs/practice-knowledge-test/Pages/default.aspx'
MN_DVS_APPOINTMENT_URL = 'https://drive.mn.gov/'

# Quiz settings
MAX_QUESTIONS_PER_QUIZ = 40
MIN_PASSING_SCORE = 80
QUIZ_TIME_LIMIT = 30  # minutes
ALLOW_QUIZ_RESUME = True
SHOW_CORRECT_ANSWERS = False
RANDOMIZE_QUESTIONS = True
RANDOMIZE_CHOICES = True

# Study materials
HELP_STUDY_MATERIALS = [
    {
        'title': 'Minnesota Driver\'s Manual',
        'description': 'Official Minnesota Driver\'s Manual - essential reading for the test.',
        'link': MN_DRIVERS_MANUAL_URL
    },
    {
        'title': 'DVS Practice Test',
        'description': 'Official online practice test from Minnesota DVS.',
        'link': MN_DVS_PRACTICE_TEST_URL
    },
    {
        'title': 'Schedule Your Test',
        'description': 'Schedule your official knowledge test with Minnesota DVS.',
        'link': MN_DVS_APPOINTMENT_URL
    }
]

# Quiz attempt settings
MAX_ATTEMPTS_PER_DAY = 3
COOLDOWN_BETWEEN_ATTEMPTS = 60  # minutes
SAVE_ATTEMPT_HISTORY = True
ATTEMPT_EXPIRY_DAYS = 30

# Question bank settings
MIN_QUESTIONS_REQUIRED = 100
QUESTION_DIFFICULTY_WEIGHTS = {
    'easy': 0.3,
    'medium': 0.5,
    'hard': 0.2
}

# Feedback settings
ALLOW_QUESTION_FEEDBACK = True
FEEDBACK_MODERATION = True
MIN_FEEDBACK_LENGTH = 10
MAX_FEEDBACK_LENGTH = 500
