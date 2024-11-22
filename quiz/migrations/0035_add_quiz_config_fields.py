from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0034_add_quiz_text_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='max_attempts',
            field=models.IntegerField(default=0, help_text='0 = unlimited attempts'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='random_order',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='quiz',
            name='answers_at_end',
            field=models.BooleanField(default=True),
        ),
    ]
