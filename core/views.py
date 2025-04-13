from django.shortcuts import render
from django.views.generic import TemplateView
from catalog.models import Item

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
                'image': 'images/Telzoe.jpg',
            },
            {
                'name': 'Tel Nai Lert Bangkok',
                'description': 'Introducing 52-suites, a 1,500-square-metre Tel Spa & Wellness centre and seven venues for dining and socialising to the city.',
                'image': 'images/Tel_nai_lert.jpg',
            },
        ],
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
        ]
    }
    return render(request, 'core/home.html', context)

def destinations(request):
    """
    Destinations page view.
    """
    # Get all items from the catalog
    items = Item.objects.all()
    
    # Map items to destination format
    destinations = []
    for item in items:
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
            'region': region
        })
    
    context = {
        'page_title': 'Destinations | Tel Resorts',
        'destinations': destinations
    }
    return render(request, 'core/destinations.html', context)

def experiences(request):
    #"""
    #Experiences page view.
    #"""
    context = {
        'page_title': 'Experiences | Tel Resorts',
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
    #"""
    #About page view.
    #"""
    context = {
        'page_title': 'About Us | Tel Resorts',
    }
    return render(request, 'about.html', context) 