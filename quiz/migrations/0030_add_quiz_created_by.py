"""Add created_by field to Quiz model."""
from django.db import migrations, models
import django.db.models.deletion


def set_default_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Quiz = apps.get_model('quiz', 'Quiz')
    # Get or create default user
    default_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    # Set all existing quizzes to default user
    Quiz.objects.filter(created_by__isnull=True).update(created_by=default_user)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('quiz', '0029_add_quiz_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_quizzes',
                to='auth.user'
            ),
        ),
        migrations.RunPython(set_default_user, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='quiz',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_quizzes',
                to='auth.user'
            ),
        ),
    ]
