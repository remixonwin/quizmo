from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0033_fix_pass_mark'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='success_text',
            field=models.TextField(blank=True, help_text='Displayed when user passes the quiz'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='fail_text',
            field=models.TextField(blank=True, help_text='Displayed when user fails the quiz'),
        ),
    ]
