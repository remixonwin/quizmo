"""Add slug field to Quiz model."""
from django.db import migrations, models
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    Quiz = apps.get_model('quiz', 'Quiz')
    for quiz in Quiz.objects.all():
        quiz.slug = slugify(quiz.title)
        quiz.save()


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0028_add_quiz_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True, null=True),
        ),
        migrations.RunPython(generate_slugs, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='quiz',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
