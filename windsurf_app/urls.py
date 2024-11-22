"""
URL configuration for windsurf_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from quiz.views.error_views import handler403, handler404, handler500
from quiz.views.monitoring_views import health_check, database_health, cache_health
from quiz.views import HelpView, FAQView

# Customize admin site
admin.site.site_header = 'Quiz Administration'
admin.site.site_title = 'Quiz Admin Portal'
admin.site.index_title = 'Quiz Management'
admin.site.site_url = None  # Removes "View Site" link

# Error handlers
handler403 = 'quiz.views.error_views.handler403'
handler404 = 'quiz.views.error_views.handler404'
handler500 = 'quiz.views.error_views.handler500'

# Redirect views
def login_redirect(request):
    next_url = request.GET.get('next', '/')
    return redirect('quiz:login')

def register_redirect(request):
    return redirect('quiz:register')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quiz.urls')),  # Include quiz URLs at root
    path('accounts/', include('django.contrib.auth.urls')),  # Add Django auth URLs
    path('accounts/login/', login_redirect),  # Redirect /accounts/login/ to quiz:login
    path('accounts/register/', register_redirect),  # Redirect /accounts/register/ to quiz:register
    path('health/', health_check, name='health_check'),
    path('health/db/', database_health, name='database_health'),
    path('health/cache/', cache_health, name='cache_health'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    pass

# Remove admin URLs from the admin documentation
admin.site.final_catch_all_view = False
