"""
Views for help and documentation pages.
"""
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from typing import Dict, Any
from ..services.help_service import HelpService
from ..settings.quiz import MN_DRIVERS_MANUAL_URL, HELP_STUDY_MATERIALS
from django.conf import settings
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required

def help_view_decorators(cls):
    """Decorator to apply common security measures to help views."""
    decorators = [
        cache_control(no_cache=True, no_store=True, must_revalidate=True),
        xframe_options_deny,
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
            'help_heading': 'Help Center',
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
            'help_heading': 'Quick Start Guide',
            'quick_start_guide': quick_start['guide'],
            'quick_start_faqs': quick_start['faqs']
        })
        return context

@help_view_decorators
class StudyMaterialsView(LoginRequiredMixin, HelpBaseView):
    """Display study materials page."""
    template_name = 'quiz/help/study_materials.html'
    login_url = reverse_lazy('quiz:login')
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        """Handle request dispatch with authentication check."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add study materials to context."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Study Materials',
            'help_heading': 'Study Materials',
            'mn_drivers_manual_url': MN_DRIVERS_MANUAL_URL,
            'study_materials': HELP_STUDY_MATERIALS,
            'study_tips': HelpService.get_study_tips()
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
            'help_heading': 'Frequently Asked Questions',
            'faqs': settings.HELP_FAQS
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
        results = HelpService.search_help(query) if query else []
        context.update({
            'title': 'Search Results',
            'help_heading': 'Search Results',
            'query': query,
            'results': results
        })
        return context

    def get(self, request, *args, **kwargs):
        """Handle GET request with optional JSON response."""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = request.GET.get('q', '')
            results = HelpService.search_help(query) if query else []
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
            'help_heading': 'Contact Support',
            'contact_info': HelpService.get_contact_info()
        })
        return context
