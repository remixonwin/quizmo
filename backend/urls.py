"""
URL configuration for hello_world project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from backend.core import views as core_views
from rest_framework.authtoken import views as token_views
from rest_framework.routers import DefaultRouter
from backend.core.views import QuizViewSet, ValidateTokenView, PasswordResetView, ResetPasswordView, CustomAuthToken  # Ensure CustomAuthToken is imported

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')

urlpatterns = [
    path("", core_views.index),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path('api/register/', CustomAuthToken.as_view(), name='api_register'),  # Example endpoint
    path('api/password-reset/confirm/', ResetPasswordView.as_view(), name='password_reset_confirm'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('api/register/', core_views.RegisterView.as_view(), name='register'),
    path('api/token/', CustomAuthToken.as_view(), name='token_obtain'),  # Single token endpoint
    path('api/validate-token/', ValidateTokenView.as_view(), name='validate_token'),
    path('api/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/password-reset/confirm/', ResetPasswordView.as_view(), name='password_reset_confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
