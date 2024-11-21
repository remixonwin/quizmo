from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0012_add_timestamps'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
