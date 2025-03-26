"""
Context processors for the patron app.
"""
from google_login.models import UserProfile

def base_template(request):
    """
    Adds the appropriate base template path to the context based on user role.
    """
    if request.user.is_authenticated:
        # Get user profile to determine user type
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'LIBRARIAN':
                return {'base_template': 'base/librarian_base.html'}
        except UserProfile.DoesNotExist:
            # If no profile exists, treat as patron
            pass
    
    # Default to patron template for guests and regular patrons
    return {'base_template': 'base/patron_base.html'} 