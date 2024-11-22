"""
Add is_active field to Question and Choice models.
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0035_add_quiz_config_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='choice',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
