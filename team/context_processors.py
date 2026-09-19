from .models import UserProfile


def pending_approvals_processor(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {'pending_count': UserProfile.objects.filter(is_approved=False).count()}
    return {'pending_count': 0}


def site_language_processor(request):
    selected = request.GET.get('lang')
    if selected in {'bg', 'en'}:
        request.session['site_language'] = selected
    return {'site_language': request.session.get('site_language', 'bg')}
