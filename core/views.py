from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from catalog.models import Item 
from collection.models import Collection, CollectionItems, CollectionAuthorizedUser
from access_request.models import AccessRequest
from django.contrib.auth import get_user_model
import json

# Create your views here.


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)

def home(request):
    """
    Homepage view.
    """
    # Get the first 2 items for featured destinations
    featured_items = Item.objects.all()[:2]
    
    # Get the next 3 items for experiences
    experience_items = Item.objects.all()[2:5]
    
    # Format featured destinations
    featured_destinations = []
    for item in featured_items:
        try:
            if item.representative_image and hasattr(item.representative_image, 'url'):
                image_path = item.representative_image.url
            else:
                image_path = 'core/images/destination-feature.jpg'
        except Exception:
            # In case of any errors with the image, use default
            image_path = 'core/images/destination-feature.jpg'


        featured_destinations.append({
            'name': item.title,
            'description': item.description or '',
            'representative_image': image_path,
            'id': item.id,
        })
    
    # Format experiences
    experiences = []
    for item in experience_items:
        try:
            if item.representative_image and hasattr(item.representative_image, 'url'):
                image_path = item.representative_image.url
            else:
                image_path = 'core/images/destination-feature.jpg'
        except Exception:
            # In case of any errors with the image, use default
            image_path = 'core/images/destination-feature.jpg'

        experiences.append({
            'name': item.title,
            'description': item.description or '',
            'representative_image': image_path,
            'id': item.id,
        })
    
    context = {
        'page_title': 'Tel Resorts, Hotels & Residences – Explore Luxury Destinations',
        'featured_destinations': featured_destinations,
        'experiences': experiences
    }
    return render(request, 'core/home.html', context)

def destinations(request):
    """
    Destinations page view.
    """
    # Get all items from the catalog
    items = Item.objects.all()
    
    # Get all collections
    collections = Collection.objects.all()
    
    # Map items to destination format
    destinations = []
    for item in items:
        # Get collections this item belongs to
        item_collections = CollectionItems.objects.filter(item=item).select_related('collection')
        
        # Check if the item is in any private collections
        is_in_private_collection = any(ci.collection.visibility == 1 for ci in item_collections)
        
        # Skip items that are in private collections
        if is_in_private_collection:
            continue
            
        collection_ids = [ci.collection.id for ci in item_collections]
        
        # Map location to region
        region = 'asia'  # default
        if item.location and 'europe' in item.location.lower():
            region = 'europe'
        elif item.location and ('america' in item.location.lower() or 'caribbean' in item.location.lower()):
            region = 'americas'
            
        # Handle image - use a safe default
        try:
            if item.representative_image and hasattr(item.representative_image, 'url'):
                image_path = item.representative_image.url
            else:
                image_path = 'images/default-destination.jpg'
        except Exception:
            # In case of any errors with the image, use default
            image_path = 'images/default-destination.jpg'
            
        destinations.append({
            'name': item.title,
            'description': item.description or '',
            'representative_image': image_path,
            'region': region,
            'collection_ids': collection_ids
        })
    
    context = {
        'page_title': 'Destinations | Tel Resorts',
        'destinations': destinations,
        'collections': collections
    }
    return render(request, 'core/destinations.html', context)

def experiences(request):
    """
    Experiences page view.
    """
    # Get all items from the catalog
    items = Item.objects.all()
    
    # Get all collections
    collections = Collection.objects.all()
    
    # Map items to destination format
    destinations = []
    for item in items:
        # Get collections this item belongs to
        item_collections = CollectionItems.objects.filter(item=item).select_related('collection')
        
        # Check if the item is in any private collections
        is_in_private_collection = any(ci.collection.visibility == 1 for ci in item_collections)
        
        # Skip items that are not in private collections
        if not is_in_private_collection:
            continue
            
        collection_ids = [ci.collection.id for ci in item_collections]
        
        # Check if user is authorized for any of the collections
        is_authorized = False
        if request.user.is_authenticated:
            # Check if user is authorized for any of this item's collections
            authorized_collections = CollectionAuthorizedUser.objects.filter(
                collection__id__in=collection_ids,
                user=request.user
            ).exists()
            is_authorized = authorized_collections
        
        # Map location to region
        region = 'asia'  # default
        if item.location and 'europe' in item.location.lower():
            region = 'europe'
        elif item.location and ('america' in item.location.lower() or 'caribbean' in item.location.lower()):
            region = 'americas'
            
        # Handle image - use a safe default
        try:
            if item.representative_image and hasattr(item.representative_image, 'url'):
                image_path = item.representative_image.url
            else:
                image_path = 'images/default-destination.jpg'
        except Exception:
            # In case of any errors with the image, use default
            image_path = 'images/default-destination.jpg'
            
        destinations.append({
            'name': item.title,
            'description': item.description or '',
            'representative_image': image_path,
            'region': region,
            'collection_ids': collection_ids,
            'has_private_collection': True,  # Since we only include items with private collections
            'is_authorized_for_user': is_authorized  # Add authorization flag
        })
    
    context = {
        'page_title': 'Experiences | Tel Resorts',
        'destinations': destinations,
        'collections': collections
    }
    return render(request, 'core/experiences.html', context)

def about(request):
    """
    About page view.
    """
    context = {
        'page_title': 'About Us | Tel Resorts',
    }
    return render(request, 'core/about.html', context)

def is_librarian(user):
    return user.is_staff or user.is_superuser or user.role == 1

@login_required
@user_passes_test(is_librarian)
def librarian_dashboard(request):
    """
    Dashboard view for librarians to manage items and collections.
    """
    # Get all items with their details
    items = Item.objects.all().select_related('created_by').prefetch_related('reviews')
    
    # Get all collections with their items
    collections = Collection.objects.all().select_related('creator').prefetch_related('collectionitems_set__item')
    
    # Get all access requests
    access_requests = AccessRequest.objects.all().select_related('user', 'collection', 'reviewed_by')
    
    # Get all users
    users = get_user_model().objects.all().order_by('date_joined')
    
    context = {
        'page_title': 'Librarian Dashboard',
        'items': items,
        'collections': collections,
        'access_requests': access_requests,
        'users': users,
    }
    return render(request, 'core/librarian_dashboard.html', context)

@login_required
@user_passes_test(is_librarian)
@require_POST
def handle_access_request(request, action, request_id):
    """Handle access request approval or denial"""
    try:
        access_request = get_object_or_404(AccessRequest, id=request_id)
        
        if action == 'approve':
            # Create CollectionAuthorizedUser entry
            CollectionAuthorizedUser.objects.create(
                collection=access_request.collection,
                user=access_request.user
            )
            # Delete the access request
            access_request.delete()
            message = 'Access request approved successfully'
        elif action == 'deny':
            # Just delete the access request
            access_request.delete()
            message = 'Access request denied successfully'
            
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500) 