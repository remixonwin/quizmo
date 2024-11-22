from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Quiz, Question, Choice
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from .settings.auth import BLACKLISTED_EMAIL_DOMAINS

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        validators=[EmailValidator()]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password1(self):
        """Validate password complexity."""
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1, self.instance)
        except ValidationError as e:
            # Convert error messages to a list of strings
            error_messages = []
            for error in e.messages:
                if 'too short' in error.lower():
                    error_messages.append('This password is too short.')
                elif 'too common' in error.lower():
                    error_messages.append('This password is too common.')
                else:
                    error_messages.append(error)
            raise ValidationError(error_messages)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")
        return password2

    def clean_email(self):
        """Validate email domain and uniqueness."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('This email address is already in use.')
            domain = email.split('@')[-1]
            if domain in BLACKLISTED_EMAIL_DOMAINS:
                raise ValidationError('This email domain is not allowed.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username already exists.')
        return username

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
