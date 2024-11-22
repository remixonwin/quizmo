from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0022_questionbank_owner_alter_questionbank_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
