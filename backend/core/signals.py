from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User  # Direct import from models

@receiver(pre_save, sender=User)
def clean_email(sender, instance, **kwargs):
    """Clean and validate the user's email before saving."""
    if instance.email:
        instance.email = instance.email.lower()