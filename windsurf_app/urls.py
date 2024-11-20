"""
URL configuration for windsurf_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from quiz import views
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from quiz.views import health_check

# Customize admin site
admin.site.site_header = 'Quiz Administration'
admin.site.site_title = 'Quiz Admin Portal'
admin.site.index_title = 'Quiz Management'
admin.site.site_url = None  # Removes "View Site" link

# Use a non-obvious admin URL and remove it from admin documentation

urlpatterns = [
    path('quiz-management-portal/', admin.site.urls),
    path('', include('quiz.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='quiz:home'), name='logout'),
    path('health/', health_check, name='health_check'),  # Primary health check endpoint with trailing slash
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler403 = 'quiz.views.handler403'
handler404 = 'quiz.views.handler404'
handler500 = 'quiz.views.handler500'

# Remove admin URLs from the admin documentation
admin.site.final_catch_all_view = False
