from .models import UserProfile

def pending_approvals_processor(request):
    # This function runs on every request and makes 'pending_count' 
    # available in all your templates automatically.
    if request.user.is_authenticated and request.user.is_staff:
        count = UserProfile.objects.filter(is_approved=False).count()
        return {'pending_count': count}
    return {'pending_count': 0}