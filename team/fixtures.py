from datetime import date, time
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404, redirect, render

from .models import Fixture


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


def _fallback_matches():
    matches = []
    for round_number, match_date, match_time, home_team, away_team, venue in DEFAULT_FIXTURES:
        matches.append(SimpleNamespace(
            round_number=round_number, match_date=match_date, match_time=match_time,
            home_team=home_team, away_team=away_team, venue=venue,
            home_score=None, away_score=None,
            is_home_match=home_team == 'ФК Марев Старс (U15)', has_result=False,
        ))
    return matches


def fixtures_view(request):
    today = date.today()
    try:
        matches = list(Fixture.objects.all())
    except (OperationalError, ProgrammingError):
        matches = _fallback_matches()
    return render(request, 'fixtures.html', {
        'upcoming_matches': [match for match in matches if match.match_date >= today],
        'past_matches': [match for match in matches if match.match_date < today],
    })


def _is_owner(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'owner')


@user_passes_test(_is_owner, login_url='team:support_login')
def fixtures_manage(request):
    try:
        matches = Fixture.objects.all()
        # Force the SQL query now, so a missing migration is handled below.
        list(matches[:1])
    except (OperationalError, ProgrammingError):
        return render(request, 'fixtures_manage.html', {
            'database_unavailable': True,
            'matches': [],
        })

    if request.method == 'POST':
        fixture = get_object_or_404(Fixture, pk=request.POST.get('fixture_id'))
        home_score = request.POST.get('home_score', '').strip()
        away_score = request.POST.get('away_score', '').strip()
        if home_score == '' and away_score == '':
            fixture.home_score = None
            fixture.away_score = None
            fixture.save(update_fields=['home_score', 'away_score', 'updated_at'])
            messages.success(request, 'Резултатът е премахнат.')
        elif home_score.isdigit() and away_score.isdigit():
            fixture.home_score = int(home_score)
            fixture.away_score = int(away_score)
            fixture.save(update_fields=['home_score', 'away_score', 'updated_at'])
            messages.success(request, 'Резултатът е запазен.')
        else:
            messages.error(request, 'Въведете два резултата с цели числа.')
        return redirect('team:fixtures_manage')
    return render(request, 'fixtures_manage.html', {
        'matches': matches,
        'database_unavailable': False,
    })
