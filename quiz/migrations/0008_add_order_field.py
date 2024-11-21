from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0007_questionbank_bankquestion_quiz_bank_bankchoice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
