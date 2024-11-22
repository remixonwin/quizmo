"""Forms for the quiz application."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm as BasePasswordResetForm, SetPasswordForm as BaseSetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from .models import Quiz, Question, Choice
from .settings.auth import BLACKLISTED_EMAIL_DOMAINS

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration."""
    
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", 'password1', 'password2')
        
    def clean_email(self):
        """Validate email domain and uniqueness."""
        email = self.cleaned_data.get('email', '').lower()
        domain = email.split('@')[1]
        
        if domain in BLACKLISTED_EMAIL_DOMAINS:
            raise ValidationError(_("This email domain is not allowed for registration."))
            
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("This email address is already in use"))
            
        return email
        
    def clean_password1(self):
        """Validate password strength."""
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1, self.instance)
            
            # Additional custom password complexity checks
            if not any(c.isupper() for c in password1):
                raise ValidationError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in password1):
                raise ValidationError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in password1):
                raise ValidationError('Password must contain at least one number')
            if not any(not c.isalnum() for c in password1):
                raise ValidationError('Password must contain at least one special character')
                
        except ValidationError as e:
            error_messages = []
            if isinstance(e.messages, list):
                for error in e.messages:
                    if 'too short' in error.lower():
                        error_messages.append('This password is too short')
                    else:
                        error_messages.append(error)
            else:
                error_messages.append(str(e))
            raise ValidationError(error_messages)
        return password1

    def clean_password2(self):
        """Validate password confirmation."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match")
        return password2

    def clean_username(self):
        """Validate username uniqueness."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username already exists')
        return username

class PasswordResetForm(BasePasswordResetForm):
    """Custom form for password reset."""
    
    def clean_email(self):
        """Clean and validate email."""
        email = self.cleaned_data['email'].lower()
        return email

class SetPasswordForm(BaseSetPasswordForm):
    """Custom form for setting new password."""
    
    def clean_new_password1(self):
        """Validate new password strength."""
        password1 = self.cleaned_data.get('new_password1')
        try:
            validate_password(password1, self.user)  # Use self.user instead of self.instance
            
            # Additional custom password complexity checks
            if not any(c.isupper() for c in password1):
                raise ValidationError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in password1):
                raise ValidationError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in password1):
                raise ValidationError('Password must contain at least one number')
            if not any(not c.isalnum() for c in password1):
                raise ValidationError('Password must contain at least one special character')
                
        except ValidationError as e:
            error_messages = []
            if isinstance(e.messages, list):
                for error in e.messages:
                    if 'too short' in error.lower():
                        error_messages.append('This password is too short')
                    else:
                        error_messages.append(error)
            else:
                error_messages.append(str(e))
            raise ValidationError(error_messages)
        return password1

    def clean_new_password2(self):
        """Validate password confirmation."""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match")
        return password2

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) > 200:
            raise forms.ValidationError('Title must be less than 200 characters.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) > 1000:
            raise forms.ValidationError('Description must be less than 1000 characters.')
        return description

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'text']

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('Question text is required.')
        return text

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['question', 'text', 'is_correct']

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('Choice text is required.')
        if len(text) > 200:
            raise forms.ValidationError('Choice text must be less than 200 characters.')
        return text
