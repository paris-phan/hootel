from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from catalog.models import ItemReview

# Create your views here.

@login_required
def profile(request):
    return redirect('accounts:user_profile', username=request.user.username)

def user_profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    is_own_profile = request.user.is_authenticated and request.user == user
    reviews = ItemReview.objects.filter(creator=user).select_related('item').order_by('-created_at')
    
    context = {
        'user': user,
        'role_display': 'Patron' if user.role == 0 else 'Librarian',
        'is_own_profile': is_own_profile,
        'reviews': reviews
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
    return redirect('accounts:user_profile', username=request.user.username)
