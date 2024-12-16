from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

@receiver(pre_save, sender=User)
def clean_email(sender, instance, **kwargs):
    """
    Clean and validate the user's email before saving.
    """
    if instance.email:
        instance.email = instance.email.lower()