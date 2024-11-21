from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0014_add_choice_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
