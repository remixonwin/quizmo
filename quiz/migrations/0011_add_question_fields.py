from django.db import migrations, models
from django.db import transaction


def initialize_order(apps, schema_editor):
    Question = apps.get_model('quiz', 'Question')
    db_alias = schema_editor.connection.alias
    
    # Use a transaction to ensure atomicity
    with transaction.atomic():
        # Group questions by quiz
        for quiz_id in Question.objects.using(db_alias).values_list('quiz', flat=True).distinct():
            # Get all questions for this quiz and order them
            quiz_questions = Question.objects.using(db_alias).filter(quiz_id=quiz_id)
            
            # First handle questions that already have an order value
            ordered_questions = quiz_questions.exclude(order=0).order_by('order')
            next_order = ordered_questions.count()
            
            # Then handle questions with order=0
            unordered_questions = quiz_questions.filter(order=0).order_by('id')
            for question in unordered_questions:
                question.order = next_order
                question.save(using=db_alias)
                next_order += 1


def reverse_order(apps, schema_editor):
    Question = apps.get_model('quiz', 'Question')
    db_alias = schema_editor.connection.alias
    
    with transaction.atomic():
        Question.objects.using(db_alias).update(order=0)


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0010_add_timestamp_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='difficulty',
            field=models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium', max_length=10),
        ),
        migrations.AddField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True, help_text='Explanation shown after answering'),
        ),
        migrations.AddField(
            model_name='question',
            name='points',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='question',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='question',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='question',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        # Run the data migration to initialize order values
        migrations.RunPython(initialize_order, reverse_order),
        # Add the unique constraint after initializing the order values
        migrations.AlterUniqueTogether(
            name='question',
            unique_together={('quiz', 'order')},
        ),
    ]
