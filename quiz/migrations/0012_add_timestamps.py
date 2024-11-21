from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0011_add_question_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizattempt',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='quizattempt',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
