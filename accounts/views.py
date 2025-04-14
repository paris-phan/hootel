from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from catalog.models import ItemReview
from loans.models import Loan

# Create your views here.

@login_required
def profile(request):
    return redirect('accounts:user_profile', username=request.user.username)

def user_profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    is_own_profile = request.user.is_authenticated and request.user == user
    reviews = ItemReview.objects.filter(creator=user).select_related('item').order_by('-created_at')
    loans = Loan.objects.filter(requester=user).select_related('item').order_by('-requested_at')
    
    context = {
        'user': user,
        'role_display': 'Patron' if user.role == 0 else 'Librarian',
        'is_own_profile': is_own_profile,
        'reviews': reviews,
        'loans': loans
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

@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_user_role(request, user_id):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            user = get_object_or_404(get_user_model(), id=user_id)
            new_role = data.get('new_role')
            
            if new_role is None:
                return JsonResponse({'success': False, 'message': 'New role not specified'})
            
            new_role = int(new_role)
            if new_role not in [0, 1]:
                return JsonResponse({'success': False, 'message': 'Invalid role value'})
            
            user.role = new_role
            user.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
