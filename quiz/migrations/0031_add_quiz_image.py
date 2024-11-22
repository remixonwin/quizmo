"""Add image field to Quiz model."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0030_add_quiz_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='quiz_images/'),
        ),
    ]
