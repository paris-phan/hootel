from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from patron.models import Hotel, HotelBooking, Collection, Item, Borrowing, CollectionAccessRequest, CollectionRoom, Room, CollectionBooking
from datetime import datetime
from django.utils import timezone
from django.db import models
from django.urls import reverse

@login_required
def create_hotel(request):
    """
    View for creating new hotels.
    """
    if request.method == 'POST':
        name = request.POST.get('name_field')
        street_address = request.POST.get('street_address_field')
        city = request.POST.get('city_field')
        state = request.POST.get('name_field')
        country = request.POST.get('country_field')
        price = request.POST.get('price_field')
        description = request.POST.get('description')
        
        if name and street_address and city and state and country and price:
            # Create the hotel instance without saving to DB yet
            hotel = Hotel(
                name=name,
                street_address=street_address,
                city=city,
                state=state,
                country=country,
                price=price,
                description=description,
                created_by=request.user
            )
            
            # Check if an image was uploaded
            if 'hotel_image' in request.FILES:
                hotel.image = request.FILES['hotel_image']
                
            # Save the hotel to the database
            hotel.save()
            
            messages.success(request, 'Hotel created successfully!')
            return redirect('manage_hotels')
        else:
            messages.error(request, 'Please provide the name, street address, city, state, country, and price for the hotel.')
    
    return render(request, 'librarian/create_hotel.html')


@login_required
def manage_hotels(request):
    """
    View for managing hotels.
    """
    # For staff, show all hotels
    if request.user.is_staff:
        hotels = Hotel.objects.all().order_by('-created_at')
    else:
        # For regular users, only show hotels they created
        hotels = Hotel.objects.filter(created_by=request.user).order_by('-created_at')
    
    return render(request, 'librarian/manage_hotels.html', {
        'hotels': hotels
    })

def edit(request, hotel_id):
    hotel = Hotel.objects.get(pk = hotel_id)
    if request.method == "POST":
        if request.POST["name_field"] != "":
            hotel.name = request.POST["name_field"]
        if request.POST["location_field"] != "":
            hotel.location = request.POST["location_field"]
        hotel.save()
        return update(request)
    return render(request, 'librarian/edit_hotel.html', {'hotel': hotel})

def delete(request, hotel_id):
    hotel = Hotel.objects.get(pk = hotel_id)
    hotel.delete()
    return update(request)

def update(request):
    hotels = Hotel.objects.all()
    hotels = hotels.filter(owner=request.user.id)
    return render(request, 'librarian/manage_hotels.html', {'hotels': hotels})
    
@require_POST
@login_required
def update_hotel_image(request, hotel_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Get the hotel and verify ownership/librarian status
            hotel = Hotel.objects.get(id=hotel_id)
            user_profile = request.user.userprofile
            
            # Only allow the owner or a librarian to update
            if hotel.owner != request.user and user_profile.user_type != 'LIBRARIAN':
                return JsonResponse({'success': False, 'error': 'Permission denied'})
            
            # Delete old image if it exists
            if hotel.image:
                hotel.image.delete(save=False)
                
            # Save the new image
            hotel.image = request.FILES.get('hotel_image')
            hotel.save()
            
            return JsonResponse({
                'success': True,
                'image_url': hotel.image_url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def update_hotel(request, hotel_id):
    """
    View for updating an existing hotel.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    # Check permissions - must be staff or the hotel creator
    if not request.user.is_staff and hotel.created_by != request.user:
        messages.error(request, "You don't have permission to update this hotel.")
        return redirect('manage_hotels')
    
    if request.method == 'POST':
        name = request.POST.get('name_field')
        location = request.POST.get('location_field')
        description = request.POST.get('description')
        
        if name and location:
            hotel.name = name
            hotel.location = location
            hotel.description = description
            
            # Check if an image was uploaded
            if 'hotel_image' in request.FILES:
                # Delete old image if it exists
                if hotel.image:
                    hotel.image.delete(save=False)
                hotel.image = request.FILES['hotel_image']
                
            hotel.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('patron:view_hotel', hotel_id=hotel.id)
        else:
            messages.error(request, 'Please provide both name and location for the hotel.')
    
    return render(request, 'librarian/update_hotel.html', {'hotel': hotel})

@login_required
def delete_hotel(request, hotel_id):
    """
    View for deleting a hotel.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    # Check permissions - must be staff or the hotel creator
    if not request.user.is_staff and hotel.created_by != request.user:
        messages.error(request, "You don't have permission to delete this hotel.")
        return redirect('manage_hotels')
    
    if request.method == 'POST':
        # Check for associated bookings
        bookings = HotelBooking.objects.filter(hotel=hotel).exists()
        
        if bookings:
            messages.warning(request, "Cannot delete hotel with associated bookings.")
            return redirect('patron:view_hotel', hotel_id=hotel.id)
        
        # Delete the hotel
        hotel_name = hotel.name
        hotel.delete()
        messages.success(request, f'Hotel "{hotel_name}" has been deleted successfully.')
        return redirect('manage_hotels')
    
    return render(request, 'librarian/delete_hotel.html', {'hotel': hotel})

@login_required
def librarian_dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'librarian/dashboard.html', context) 