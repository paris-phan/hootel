from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from catalog.models import ItemReview, Item
from loans.models import Loan
from collection.models import CollectionAuthorizedUser
from access_request.models import AccessRequest
from core.views import is_librarian

# Create your views here.

@login_required
def profile(request):
    return redirect('accounts:user_profile', username=request.user.username)

def user_profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    is_own_profile = request.user.is_authenticated and request.user == user
    reviews = ItemReview.objects.filter(creator=user).select_related('item').order_by('-created_at')
    loans = Loan.objects.filter(requester=user).select_related('item').order_by('-requested_at')
    
    # Get authorized collections and access requests
    authorized_collections = CollectionAuthorizedUser.objects.filter(user=user).select_related('collection')
    access_requests = AccessRequest.objects.filter(user=user).select_related('collection')
    
    # Combine data for exclusive access section
    exclusive_access_data = {
        'authorized': authorized_collections,
        'requests': access_requests
    }
    
    # Get all items for the collection creation modal if this is the user's own profile
    all_items = Item.objects.all() if is_own_profile else None
    
    context = {
        'user': user,
        'role_display': 'Patron' if user.role == 0 else 'Librarian',
        'is_own_profile': is_own_profile,
        'reviews': reviews,
        'loans': loans,
        'authorized_collections': authorized_collections,
        'access_requests': access_requests,
        'exclusive_access_data': exclusive_access_data,
        'all_items': all_items
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
def cancel_access_request(request, request_id):
    """Cancel an access request made by the current user"""
    if request.method == 'POST':
        access_request = get_object_or_404(AccessRequest, id=request_id)
        
        # Ensure the request belongs to the current user
        if access_request.user != request.user:
            return HttpResponseForbidden("You don't have permission to cancel this request")
        
        # Only allow cancelling pending requests
        if access_request.status != 'pending':
            messages.error(request, "Only pending requests can be cancelled")
            return redirect('accounts:user_profile', username=request.user.username)
        
        # Delete the request
        access_request.delete()
        messages.success(request, "Access request cancelled successfully")
        
    return redirect('accounts:user_profile', username=request.user.username)

@login_required
@user_passes_test(is_librarian)
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
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
