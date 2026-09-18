from django.shortcuts import render


def fixtures_view(request):
    return render(request, 'fixtures.html')
