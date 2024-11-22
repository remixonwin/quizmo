"""
Views for help and documentation pages.
"""
from typing import Dict, Any
from django.views.generic import TemplateView
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from ..services.help_service import HelpService

def help_view_decorators(cls):
    """Decorator to apply common security measures to help views."""
    decorators = [
        cache_control(no_cache=True, no_store=True, must_revalidate=True),
        xframe_options_deny,
        csrf_protect,
        require_http_methods(["GET"])
    ]
    for decorator in decorators:
        cls = method_decorator(decorator, name='dispatch')(cls)
    return cls

class HelpBaseView(TemplateView):
    """Base view for help pages."""
    
    def get_context_data(self, **kwargs):
        """Add common context data for help pages."""
        context = super().get_context_data(**kwargs)
        context.update({
            'meta_description': 'Access comprehensive study materials and tips for the Minnesota DMV Practice Quiz',
            'help_sections': HelpService.get_help_sections()
        })
        return context

@help_view_decorators
class HelpView(HelpBaseView):
    """Display help center page."""
    template_name = 'quiz/help/help.html'
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add help content to context."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Help Center',
            'sections': HelpService.get_help_sections()
        })
        return context

@help_view_decorators
class QuickStartView(HelpBaseView):
    """Display quick start guide page."""
    template_name = 'quiz/help/quick_start.html'
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add quick start guide content to context."""
        context = super().get_context_data(**kwargs)
        quick_start = HelpService.get_quick_start_guide()
        context.update({
            'title': 'Quick Start Guide',
            'quick_start_guide': quick_start['guide'],
            'quick_start_faqs': quick_start['faqs']
        })
        return context

@help_view_decorators
class StudyMaterialsView(HelpBaseView):
    """Display study materials page."""
    template_name = 'quiz/help/study_materials.html'
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add study materials to context."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Study Materials',
            'study_materials': [
                {
                    'title': 'Minnesota Driver\'s Manual',
                    'description': 'Official study guide from the Minnesota Department of Public Safety.',
                    'link': settings.MN_DRIVERS_MANUAL_URL,
                    'icon': 'book'
                },
                {
                    'title': 'Road Signs Guide',
                    'description': 'Learn Minnesota road signs and traffic signals.',
                    'link': reverse('quiz:help_road_signs'),
                    'icon': 'traffic-light'
                }
            ],
            'study_tips': [
                {
                    'title': 'Review Regularly',
                    'description': 'Set aside time each day to study Minnesota traffic laws.',
                    'icon': 'calendar'
                },
                {
                    'title': 'Track Progress',
                    'description': 'Monitor your scores to identify areas for improvement.',
                    'icon': 'chart-line'
                }
            ]
        })
        return context

@help_view_decorators
class FAQView(HelpBaseView):
    """Display FAQ page."""
    template_name = 'quiz/help/faq.html'
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add FAQs to context."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Frequently Asked Questions',
            'categories': settings.HELP_FAQS,
            'meta_description': 'Find answers to common questions about the Minnesota DMV Practice Quiz'
        })
        return context

@help_view_decorators
class HelpSearchView(HelpBaseView):
    """Display help search results page."""
    template_name = 'quiz/help/search.html'
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add search results to context."""
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context.update({
            'title': 'Help Search Results',
            'query': query,
            'results': HelpService.search_help_content(query) if query else []
        })
        return context
    
    def get(self, request, *args, **kwargs):
        """Handle GET request with optional JSON response."""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = request.GET.get('q', '')
            results = HelpService.search_help_content(query) if query else []
            return JsonResponse({'results': results})
        return super().get(request, *args, **kwargs)

@help_view_decorators
class HelpContactView(HelpBaseView):
    """Display help contact page."""
    template_name = 'quiz/help/contact.html'
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add contact information to context."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Contact Support',
            'contact_info': {
                'email': settings.SUPPORT_EMAIL,
                'hours': 'Monday - Friday, 9:00 AM - 5:00 PM CST',
                'response_time': '24-48 hours'
            }
        })
        return context
