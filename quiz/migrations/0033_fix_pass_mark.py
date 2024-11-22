from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0032_add_quiz_dates'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='passing_score',
            new_name='pass_mark',
        ),
    ]
