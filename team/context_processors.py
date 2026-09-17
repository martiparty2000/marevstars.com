from .models import UserProfile


def pending_approvals_processor(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {'pending_count': UserProfile.objects.filter(is_approved=False).count()}
    return {'pending_count': 0}
