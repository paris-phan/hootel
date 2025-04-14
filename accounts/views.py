from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

# Create your views here.

@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
        'role_display': 'Patron' if user.role == 0 else 'Librarian'
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def update_profile_photo(request):
    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            user = request.user
            user.profile_picture = request.FILES['profile_picture']
            user.save()
            messages.success(request, 'Profile picture updated successfully!')
        else:
            messages.error(request, 'No file was uploaded.')
    return redirect('accounts:profile')
