from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0013_add_choice_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
