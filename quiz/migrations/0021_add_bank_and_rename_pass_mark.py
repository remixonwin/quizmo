"""
Migration to rename pass_mark to passing_score and add tags field to QuestionBank.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0020_choice_created_at_choice_updated_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='pass_mark',
            new_name='passing_score',
        ),
        migrations.AddField(
            model_name='questionbank',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quiz',
            name='bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quizzes', to='quiz.questionbank'),
        ),
    ]
