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
        'page_title': 'Aman Resorts, Hotels & Residences – Explore Luxury Destinations',
        'featured_destinations': [
            {
                'name': 'Amanzoe, Greece',
                'description': 'Amanzoe welcomes a new season on the beach-fringed Peloponnese.',
                'image': 'images/amanzoe.jpg',
            },
            {
                'name': 'Aman Nai Lert Bangkok',
                'description': 'Introducing 52-suites, a 1,500-square-metre Aman Spa & Wellness centre and seven venues for dining and socialising to the city.',
                'image': 'images/aman_nai_lert.jpg',
            },
        ],
        'experiences': [
            {
                'name': 'Wellness Journeys',
                'description': 'Embark on a path to wellbeing with Aman\'s immersive wellness programs.',
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
        if 'europe' in item.location.lower():
            region = 'europe'
        elif 'america' in item.location.lower() or 'caribbean' in item.location.lower():
            region = 'americas'
            
        destinations.append({
            'name': item.title,
            'description': item.description,
            'image': item.representative_image.url if item.representative_image else 'images/default-destination.jpg',
            'region': region
        })
    
    context = {
        'page_title': 'Destinations | Aman Resorts',
        'destinations': destinations
    }
    return render(request, 'core/destinations.html', context)

def experiences(request):
    #"""
    #Experiences page view.
    #"""
    context = {
        'page_title': 'Experiences | Aman Resorts',
        'experiences': [
            {
                'name': 'Wellness Journeys',
                'description': 'Embark on a path to wellbeing with Aman\'s immersive wellness programs.',
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
        'page_title': 'About Us | Aman Resorts',
    }
    return render(request, 'about.html', context) 