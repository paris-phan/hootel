from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.forms import ValidationError

class NoUsernamePasswordAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True
    
    def save_user(self, request, user, form, commit=True):
        raise ValidationError("Direct signups are disabled. Please use Google Sign-In only.")
    
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True
    
    def save_user(self, request, sociallogin, form):
        user = super().save_user(request, sociallogin, form)
        