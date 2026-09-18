from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .models import Fixture


def fixtures_view(request):
    matches = Fixture.objects.all()
    today = date.today()
    return render(request, 'fixtures.html', {
        'upcoming_matches': matches.filter(match_date__gte=today),
        'past_matches': matches.filter(match_date__lt=today),
    })


def _is_owner(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'owner')


@user_passes_test(_is_owner, login_url='team:support_login')
def fixtures_manage(request):
    matches = Fixture.objects.all()
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
    return render(request, 'fixtures_manage.html', {'matches': matches})
