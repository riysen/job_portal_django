from .models import UserProfile

def user_profile(request):
    """Add user profile to template context"""
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return {'user_type': profile.user_type}
        except UserProfile.DoesNotExist:
            return {'user_type': 'applicant'}
    return {'user_type': None}