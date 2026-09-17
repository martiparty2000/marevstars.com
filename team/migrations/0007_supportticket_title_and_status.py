from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('team', '0006_alter_userprofile_role')]
    operations = [
        migrations.AddField(model_name='supportticket', name='title', field=models.CharField(default='Ново запитване', max_length=120)),
        migrations.AlterField(model_name='supportticket', name='status', field=models.CharField(choices=[('active', 'Ново'), ('handled', 'В процес'), ('archived', 'Архивирано')], default='active', max_length=12)),
    ]
