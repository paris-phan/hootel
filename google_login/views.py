from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from allauth.socialaccount.models import SocialApp

# added these for login redirection 
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.views.decorators.http import require_POST

def home(request):
    if not request.user.is_authenticated:
        # Show guest home page instead of redirecting to login
        return render(request, "google_login/guest_home.html", {
            'title': 'Welcome to HotelManager6000'
        })
        
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'user_type': 'PATRON'}
    )
    
    context = {
        'name': request.user.username,
        'email': request.user.email,
        'user_type': user_profile.user_type,
        'profile_picture': user_profile.profile_picture,
        'profile_picture_url': user_profile.profile_picture_url
    }
    
    # Handle user types
    if user_profile.user_type == 'PATRON':
        return render(request, "google_login/patron_home.html", context)
    else:
        return render(request, "google_login/librarian_home.html", context)


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
        
    # Check if Google app is configured
    if not SocialApp.objects.filter(provider='google').exists():
        messages.error(request, 'Google authentication is not configured properly.')
        
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('/')
    else:
        form = AuthenticationForm()

    return render(request, "google_login/login.html", {
        "form": form,
    })

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')

@require_POST
@login_required
def update_profile_picture(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Delete old profile picture if it exists to avoid storage buildup
            if user_profile.profile_picture:
                user_profile.profile_picture.delete(save=False)
                
            # Save the new profile picture
            user_profile.profile_picture = request.FILES.get('profile_picture')
            user_profile.save()
            
            return JsonResponse({
                'success': True,
                'image_url': user_profile.profile_picture_url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'})