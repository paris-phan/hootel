from django.shortcuts import render
from django.views.generic import TemplateView
from catalog.models import Item 
from collection.models import Collection, CollectionItems
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)

def home(request):
    """
    Homepage view.
    """
    context = {
        'page_title': 'Tel Resorts, Hotels & Residences – Explore Luxury Destinations',
        'featured_destinations': [
            {
                'name': 'Telzoe, Greece',
                'description': 'Telzoe welcomes a new season on the beach-fringed Peloponnese.',
                'image': 'core/images/destination-feature.jpg',
            },
            {
                'name': 'Tel Nai Lert Bangkok',
                'description': '"Introducing 52-suites, a 1,500-square-metre Tel Spa & Wellness centre and seven venues for dining and socialising to the city. Tel Nai Lert blends timeless Thai elegance with modern sophistication. Each suite is thoughtfully designed to reflect the rich cultural heritage of the Nai Lert Park area while offering state-of-the-art comfort. The Tel Spa & Wellness centre provides a sanctuary for holistic rejuvenation, featuring bespoke treatments and serene spaces. With seven distinct dining and social venues, guests can explore a vibrant tapestry of flavors and experiences that celebrate both local and international culinary artistry.',
                'image': 'core/images/destination-feature.jpg',
            },
        ],
        'experiences': [
            {
                'name': 'Wellness Journeys',
                'description': 'Embark on a path to wellbeing with Tel\'s immersive wellness programs.',
                'image': 'core/images/destination-feature.jpg',
            },
            {
                'name': 'Cultural Discoveries',
                'description': 'Immerse yourself in local traditions and authentic cultural experiences.',
                'image': 'core/images/destination-feature.jpg',
            },
            {
                'name': 'Active Adventures',
                'description': 'Explore dramatic landscapes and natural wonders with expert guides.',
                'image': 'core/images/destination-feature.jpg',
            },
        ]
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
    #"""
    #Experiences page view.
    #"""
    # Get all collections
    collections = Collection.objects.all()
    
    context = {
        'page_title': 'Experiences | Tel Resorts',
        'collections': collections,
        'experiences': [
            {
                'name': 'Wellness Journeys',
                'description': 'Embark on a path to wellbeing with Tel\'s immersive wellness programs.',
                'image': 'images/experiences-1.jpg',
            },
            {
                'name': 'Cultural Discoveries',
                'description': 'Immerse yourself in local traditions and authentic cultural experiences.',
                'image': 'images/experiences-2.jpg',
            },
            {
                'name': 'Active Adventures',
                'description': 'Explore dramatic landscapes and natural wonders with expert guides.',
                'image': 'images/experiences-3.jpg',
            },
            # Add more experiences here
        ]
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
    return user.is_staff or user.is_superuser

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
    
    context = {
        'page_title': 'Librarian Dashboard',
        'items': items,
        'collections': collections,
    }
    return render(request, 'core/librarian_dashboard.html', context) 