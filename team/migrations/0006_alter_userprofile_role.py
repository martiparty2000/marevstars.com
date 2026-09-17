from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('team', '0005_supportticket_supportmessage')]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('player', 'Player'),
                    ('coach', 'Coach'),
                    ('head_coach', 'Head Coach'),
                    ('owner', 'Owner'),
                ],
                default='player',
                max_length=15,
            ),
        ),
    ]
