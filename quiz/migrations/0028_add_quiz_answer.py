"""Add QuizAnswer model and metadata fields."""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0027_quiz_time_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='question',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='choice',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='quizattempt',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.CreateModel(
            name='QuizAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quiz.quizattempt')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.choice')),
            ],
            options={
                'ordering': ['question__order', 'created_at'],
                'unique_together': {('attempt', 'question')},
            },
        ),
    ]
