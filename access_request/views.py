from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import AccessRequest
from collection.models import Collection, CollectionAuthorizedUser
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

def is_librarian(user):
    return user.is_staff

# Create your views here.

@login_required
@require_POST
def create_access_request(request):
    collection_id = request.POST.get('collection_id')
    reason = request.POST.get('reason', '')
    
    try:
        collection = Collection.objects.get(id=collection_id)
        
        # Check if user already has a pending request
        existing_request = AccessRequest.objects.filter(
            user=request.user,
            collection=collection,
            status='pending'
        ).exists()
        
        if existing_request:
            return JsonResponse({
                'success': False,
                'message': 'You already have a pending request for this collection'
            })
        
        # Create new access request
        access_request = AccessRequest.objects.create(
            user=request.user,
            collection=collection,
            reason=reason
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Access request submitted successfully'
        })
        
    except Collection.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Collection not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@user_passes_test(is_librarian)
@require_POST
def approve_access_request(request, request_id):
    try:
        access_request = get_object_or_404(AccessRequest, id=request_id)
        
        # Create CollectionAuthorizedUser entry
        CollectionAuthorizedUser.objects.create(
            collection=access_request.collection,
            user=access_request.user
        )
        
        # Delete the access request
        access_request.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Access request approved successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@user_passes_test(is_librarian)
@require_POST
def deny_access_request(request, request_id):
    try:
        access_request = get_object_or_404(AccessRequest, id=request_id)
        access_request.deny(request.user)
        return JsonResponse({
            'success': True,
            'message': 'Access request denied successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
