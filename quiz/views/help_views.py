"""
Views for help and documentation pages.
"""
from django.views.generic import TemplateView
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect


@method_decorator([
    cache_control(no_cache=True, no_store=True, must_revalidate=True),
    xframe_options_deny,
    csrf_protect,
    require_http_methods(["GET"])
], name='dispatch')
class HelpView(TemplateView):
    template_name = 'quiz/help/help.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')

        # Basic page information
        context.update({
            'title': 'Help Center',
            'page_title': 'Help Center',
            'search_query': search_query,
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'support@example.com'),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', None),
            'meta_description': 'Get help with the Minnesota DMV Practice Quiz. Find answers to frequently asked questions and learn how to use the practice tests effectively.',
        })

        # Quick start guide
        context['quick_start'] = [
            {
                'title': 'Create an Account',
                'description': 'Sign up for free to track your progress and save your scores.'
            },
            {
                'title': 'Choose a Test',
                'description': 'Select from our practice tests based on the latest MN DMV manual.'
            },
            {
                'title': 'Take Practice Tests',
                'description': 'Answer questions and get instant feedback on your performance.'
            },
            {
                'title': 'Review Results',
                'description': 'See detailed explanations and track your improvement over time.'
            }
        ]

        # Study materials
        context['study_materials'] = [
            {
                'title': 'Minnesota Driver\'s Manual',
                'description': 'Official state manual with all the information you need to know.',
                'url': 'https://dps.mn.gov/divisions/dvs/forms-documents/Documents/Minnesota_Drivers_Manual.pdf'
            },
            {
                'title': 'Road Signs Study Guide',
                'description': 'Learn about all the road signs you need to know for the test.',
                'url': '#'
            },
            {
                'title': 'Practice Test Tips',
                'description': 'Tips and strategies for taking practice tests effectively.',
                'url': '#'
            }
        ]

        # FAQs
        context['faqs'] = [
            {
                'question': 'How do I create an account?',
                'answer': 'Click the "Register" link in the top right corner, fill out the registration form with your email and password, and click "Sign Up". You\'ll receive a confirmation email to activate your account.'
            },
            {
                'question': 'How are quizzes scored?',
                'answer': 'Quizzes are scored immediately after completion. Each question is worth one point, and you\'ll see detailed explanations for all answers.'
            },
            {
                'question': 'What is the passing score?',
                'answer': 'You need to score at least 80% (32 out of 40 questions) to pass.'
            },
            {
                'question': 'Can I review my answers?',
                'answer': 'Yes! After completing a quiz, you can review all your answers, see which ones were correct or incorrect, and read detailed explanations for each question.'
            }
        ]

        return context

    def dispatch(self, request, *args, **kwargs):
        """Add security headers to the response."""
        response = super().dispatch(request, *args, **kwargs)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


@method_decorator([
    cache_control(private=True, max_age=3600),
    xframe_options_deny,
    csrf_protect,
    require_http_methods(["GET"])
], name='dispatch')
class FAQView(TemplateView):
    """Display frequently asked questions page."""
    template_name = 'quiz/help/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Frequently Asked Questions'
        context['page_title'] = 'FAQ'
        context['meta_description'] = 'Frequently asked questions about the Minnesota DMV Practice Quiz. Find answers to common questions about practice tests, scoring, and test preparation.'
        return context

    def dispatch(self, request, *args, **kwargs):
        """Add security headers to the response."""
        response = super().dispatch(request, *args, **kwargs)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        return response
