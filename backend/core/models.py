from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "This email is already registered. Please try logging in instead.",
            'invalid': "Please enter a valid email address (e.g., name@example.com)"
        }
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': "This username is taken. Please choose another one."
        },
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

# ...existing models...

class Quiz(models.Model):
    # ...existing fields...
    pass

class Question(models.Model):
    # ...existing fields...
    pass

class Choice(models.Model):
    # ...existing fields...
    pass