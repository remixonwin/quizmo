from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_add_order_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='pass_mark',
            field=models.FloatField(default=70.0),
        ),
        migrations.AddField(
            model_name='quiz',
            name='time_limit',
            field=models.IntegerField(default=30, help_text='Time limit in minutes'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='randomize_questions',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='show_answers',
            field=models.BooleanField(default=False, help_text='Show correct answers after completion'),
        ),
    ]
