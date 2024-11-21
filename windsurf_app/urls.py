"""
URL configuration for windsurf_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from quiz.views.error_views import handler403, handler404, handler500
from quiz.views.monitoring_views import health_check, database_health, cache_health
from quiz.views import HelpView, FAQView, register
from quiz.views.quiz_views import QuizListView
from quiz.views.auth_views import logout_view

# Customize admin site
admin.site.site_header = 'Quiz Administration'
admin.site.site_title = 'Quiz Admin Portal'
admin.site.index_title = 'Quiz Management'
admin.site.site_url = None  # Removes "View Site" link

# Error handlers
handler403 = 'quiz.views.error_views.handler403'
handler404 = 'quiz.views.error_views.handler404'
handler500 = 'quiz.views.error_views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', QuizListView.as_view(), name='home'),
    path('quiz/', include('quiz.urls')),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('health/', health_check, name='health_check'),
    path('health/db/', database_health, name='database_health'),
    path('health/cache/', cache_health, name='cache_health'),
    path('help/', HelpView.as_view(), name='help'),
    path('faq/', FAQView.as_view(), name='faq'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Remove admin URLs from the admin documentation
admin.site.final_catch_all_view = False
