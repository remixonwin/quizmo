"""
Content test settings.
"""

# Minnesota DMV Manual URL
MN_DRIVERS_MANUAL_URL = 'https://dps.mn.gov/divisions/dvs/forms-documents/Documents/Minnesota_Drivers_Manual.pdf'

# Contact Information
CONTACT_EMAIL = 'support@example.com'
SUPPORT_PHONE = '+1-555-123-4567'

# Help content configuration
HELP_QUICK_START = [
    {
        'title': 'Creating an Account',
        'description': 'Register with your email to start practicing.'
    },
    {
        'title': 'Taking a Quiz',
        'description': 'Select a quiz and answer the questions.'
    }
]

HELP_STUDY_MATERIALS = [
    {
        'title': 'Minnesota Driver\'s Manual',
        'description': 'Official Minnesota Driver\'s Manual - essential reading for the test.',
        'link': MN_DRIVERS_MANUAL_URL
    },
    {
        'title': 'Study Guides',
        'description': 'Comprehensive study materials for each quiz topic.'
    },
    {
        'title': 'Practice Questions',
        'description': 'Sample questions to help you prepare for quizzes.'
    }
]

HELP_STUDY_TIPS = [
    {
        'title': 'Review Regularly',
        'description': 'Set aside time each day to practice.'
    },
    {
        'title': 'Track Progress',
        'description': 'Monitor your scores to identify areas for improvement.'
    }
]

HELP_FAQS = [
    {
        'category': 'General',
        'questions': [
            {
                'question': 'How many questions are in each quiz?',
                'answer': 'Each quiz typically contains 20-25 questions.'
            },
            {
                'question': 'How much time do I have?',
                'answer': 'Most quizzes have a 30-minute time limit.'
            }
        ]
    },
    {
        'category': 'Scoring',
        'questions': [
            {
                'question': 'What is the passing score?',
                'answer': 'You need to score 80% or higher to pass.'
            },
            {
                'question': 'Can I retake a quiz?',
                'answer': 'Yes, you can retake quizzes as many times as you want.'
            }
        ]
    }
]

HELP_CONTACT_INFO = {
    'email': 'support@example.com',
    'phone': '1-800-555-0123',
    'hours': 'Monday to Friday, 9 AM to 5 PM',
    'support_url': '/help/contact'
}
