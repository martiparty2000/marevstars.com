from datetime import date, time

from django.db import migrations, models


FIXTURES = [
    (2, date(2026, 9, 20), time(13, 0), 'ФК Марев Старс (U15)', 'ФК „Волов – Шумен 2007“ (U15)', 'Спортпалас'),
    (3, date(2026, 9, 27), time(10, 0), 'ФК Фратрия (U15)', 'ФК Марев Старс (U15)', ''),
    (4, date(2026, 10, 4), time(10, 0), 'ФК Марев Старс (U15)', 'ПФК Черно море (U15)', 'Спортпалас'),
    (5, date(2026, 10, 11), time(10, 0), 'ФК Добруджа 1919 (U15)', 'ФК Марев Старс (U15)', ''),
    (6, date(2026, 10, 18), time(11, 0), 'ФК Марев Старс (U15)', 'ФК Дунав от Русе (U15)', 'Спортпалас'),
    (7, date(2026, 10, 26), time(13, 0), 'ПФК Лудогорец 1945 (U15)', 'ФК Марев Старс (U15)', ''),
    (8, date(2026, 11, 2), time(13, 0), 'ФК Марев Старс (U15)', 'ФК Аксаково (U15)', 'Спортпалас'),
    (9, date(2026, 11, 8), time(13, 0), 'ФК „Светкавица – 2014“ (U15)', 'ФК Марев Старс (U15)', ''),
    (10, date(2026, 11, 15), time(13, 0), 'ФК Марев Старс (U15)', 'ФК Спартак 1918 (U15)', 'Спортпалас'),
    (11, date(2026, 11, 22), time(10, 0), 'ФК Олимпик (U15)', 'ФК Марев Старс (U15)', ''),
]


def add_fixtures(apps, schema_editor):
    Fixture = apps.get_model('team', 'Fixture')
    for round_number, match_date, match_time, home_team, away_team, venue in FIXTURES:
        Fixture.objects.get_or_create(round_number=round_number, defaults={
            'match_date': match_date, 'match_time': match_time, 'home_team': home_team,
            'away_team': away_team, 'venue': venue,
        })


class Migration(migrations.Migration):
    dependencies = [('team', '0007_supportticket_title_and_status')]

    operations = [
        migrations.CreateModel(
            name='Fixture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.PositiveSmallIntegerField(unique=True)),
                ('match_date', models.DateField()),
                ('match_time', models.TimeField()),
                ('home_team', models.CharField(max_length=120)),
                ('away_team', models.CharField(max_length=120)),
                ('venue', models.CharField(blank=True, max_length=120)),
                ('home_score', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('away_score', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['match_date', 'match_time']},
        ),
        migrations.RunPython(add_fixtures, migrations.RunPython.noop),
    ]
