from datetime import date, time
from types import SimpleNamespace

from django.shortcuts import render


DEFAULT_FIXTURES = [
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


def fixtures_view(request):
    today = date.today()
    upcoming_matches = [
        SimpleNamespace(
            round_number=round_number,
            match_date=match_date,
            match_time=match_time,
            home_team=home_team,
            away_team=away_team,
            venue=venue,
            is_home_match=home_team == 'ФК Марев Старс (U15)',
        )
        for round_number, match_date, match_time, home_team, away_team, venue in DEFAULT_FIXTURES
        if match_date >= today
    ]
    return render(request, 'fixtures.html', {'upcoming_matches': upcoming_matches})
