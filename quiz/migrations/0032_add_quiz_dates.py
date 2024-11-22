from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0031_add_quiz_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
