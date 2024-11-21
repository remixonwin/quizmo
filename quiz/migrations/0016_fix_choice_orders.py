from django.db import migrations

def fix_choice_orders(apps, schema_editor):
    Choice = apps.get_model('quiz', 'Choice')
    Question = apps.get_model('quiz', 'Question')
    
    # Get all questions
    for question in Question.objects.all():
        # Get all choices for this question and update their order
        choices = Choice.objects.filter(question=question).order_by('id')
        for index, choice in enumerate(choices):
            choice.order = index
            choice.save()

def reverse_fix_choice_orders(apps, schema_editor):
    # No need to reverse this migration
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0015_add_choice_tags'),  # Update this to your last migration
    ]

    operations = [
        migrations.RunPython(fix_choice_orders, reverse_fix_choice_orders),
    ]
