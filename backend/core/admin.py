from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.authtoken.models import Token
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Customize the admin interface for the User model if needed
    pass

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created']
    search_fields = ['key', 'user__username', 'user__email']

# ...existing admin registrations...