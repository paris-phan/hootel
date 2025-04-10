from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from patron.models import Hotel, HotelBooking, Collection
from datetime import datetime
from django.utils import timezone
from django.db import models
from django.urls import reverse

hotel_data = {"room number": 1, 
              "floor number": 1, 
              "square footage": 1, 
              "maximum number of occupants": 1, 
              "number of beds": 1, 
              "number of bathrooms": 1,
              "price": 0.01,
              "description": ""
            }

@login_required
def create_hotel(request):
    """
    View for creating new hotels.
    """
    if request.method == 'POST':
        for field in hotel_data.keys():
            user_response = request.POST.get(field)
            if user_response != None:
                hotel_data[field] = user_response
            else:
                messages.error(request, 'Please provide the ' + field + ' of the hotel.')
                return render(request, 'librarian/create_hotel.html')
        save_hotel(request)
   
    return render(request, 'librarian/create_hotel.html')

def save_hotel(request):
    # Create the hotel instance without saving to DB yet
    hotel = Hotel(
        room=hotel_data["room number"],
        floor=hotel_data["floor number"],
        square_footage=hotel_data["square footage"],
        max_num_of_occupants=hotel_data["maximum number of occupants"],
        num_of_beds=hotel_data["number of beds"],
        num_of_bathrooms=hotel_data["number of bathrooms"],
        price=hotel_data["price"],
        description=hotel_data["description"],
        created_by=request.user
    )

    # Check if an image was uploaded
    if 'hotel_image' in request.FILES:
        hotel.image = request.FILES['hotel_image']
                
    # Save the hotel to the database
    hotel.save()
            
    messages.success(request, 'Hotel created successfully!')
    return render(request, 'librarian/manage_hotels.html')


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
        room = request.POST.get('room_field')
        street_address = request.POST.get('street_address_field')
        city = request.POST.get('city_field')
        state = request.POST.get('state_field')
        country = request.POST.get('country_field')
        price = request.POST.get('price_field')
        description = request.POST.get('description')
        
        if room and street_address and city and state and country and price:
            # Update the hotel instance without saving to DB yet
            hotel.room=room
            hotel.street_address=street_address
            hotel.city=city
            hotel.state=state
            hotel.country=country
            hotel.price=price
            hotel.description=description
            
            # Check if an image was uploaded
            if 'hotel_image' in request.FILES:
                # Delete old image if it exists
                if hotel.image:
                    hotel.image.delete(save=False)
                hotel.image = request.FILES['hotel_image']

            # Save the hotel to the database
            hotel.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('view_hotel', hotel_id=hotel.id)
        else:
            messages.error(request, 'Please provide the room, street address, city, state, country, and price for the hotel.')     
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
        hotel_room = hotel.room
        hotel.delete()
        messages.success(request, f'Hotel "{hotel_room}" has been deleted successfully.')
        return redirect('manage_hotels')
    
    return render(request, 'librarian/delete_hotel.html', {'hotel': hotel})

@login_required
def librarian_dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'librarian/dashboard.html', context)

@login_required
def my_borrowed_items(request):
    """
    View for librarians to see their borrowed items.
    """
    # Only staff can access this page
    if not request.user.is_staff:
        messages.error(request, "Only librarians can access this page.")
        return redirect('home')
    
    # Get all borrowings for the current user
    all_borrowings = Borrowing.objects.filter(
        user=request.user
    ).order_by('-request_date')
    
    # Separate current (active) borrowings from past borrowings
    current_borrowings = all_borrowings.filter(
        status__in=['PENDING', 'APPROVED'],
        return_date__isnull=True
    )
    
    past_borrowings = all_borrowings.filter(
        models.Q(status='REJECTED') | 
        models.Q(status='RETURNED') | 
        models.Q(return_date__isnull=False)
    )
    
    return render(request, 'librarian/my_borrowed_items.html', {
        'borrowings': all_borrowings,  # Keep for backward compatibility
        'current_borrowings': current_borrowings,
        'past_borrowings': past_borrowings
    })

@login_required
def request_item_borrow(request, item_id):
    """
    View for librarians to request to borrow an item.
    """
    # Only staff can access this page
    if not request.user.is_staff:
        messages.error(request, "Only librarians can borrow items.")
        return redirect('home')
    
    item = get_object_or_404(Item, id=item_id)
    
    # Check if user already has a pending or approved request
    existing_request = Borrowing.objects.filter(
        user=request.user,
        item=item,
        status__in=['PENDING', 'APPROVED']
    ).first()
    
    if existing_request:
        if existing_request.status == 'PENDING':
            messages.info(request, "You already have a pending request for this item.")
        else:
            messages.info(request, "You are currently borrowing this item.")
    else:
        # Create new borrow request
        Borrowing.objects.create(
            user=request.user,
            item=item
        )
        messages.success(request, "Your borrowing request has been submitted.")
    
    return redirect('librarian:view_item', item_id=item.id)

@login_required
def view_item(request, item_id):
    """
    View for librarians to view item details.
    """
    # Only staff can access this page
    if not request.user.is_staff:
        messages.error(request, "Only librarians can access this page.")
        return redirect('home')
    
    item = get_object_or_404(Item, id=item_id)
    
    # Get current borrowing status
    borrowing = Borrowing.objects.filter(
        user=request.user,
        item=item
    ).order_by('-request_date').first()
    
    return render(request, 'librarian/view_item.html', {
        'item': item,
        'borrowing': borrowing
    }) 

@login_required
def search_rooms(request):
    """
    View for librarians to search for hotels.
    This view always uses the librarian interface.
    """
    # Only staff can access this page
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('patron:search')
    
    query = request.GET.get('query', '').strip()
    sort_by = request.GET.get('sort_by', '')
    num_people = request.GET.get('num_people', '')
    price = request.GET.get('price_per_night', '')

    # Get all hotels
    hotels = Hotel.objects.annotate(average_rating=Avg('review__rating'))
    for hotel in hotels:
        hotel.average_rating = hotel.review_set.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        print(hotel.average_rating)
    
    # Apply search filter if query exists
    if query:
        hotels = hotels.filter(
            Q(room__icontains=query) | 
            Q(location__icontains=query) | 
            Q(description__icontains=query)
        )

    if sort_by == 'rating':
        hotels = hotels.order_by('-average_rating', '-created_at')  # Highest rating first
    else:  # Default to numerically by room number if 'numerically by room number' is selected
        hotels = hotels.order_by('room')

    if num_people != '👥 Travelers' and num_people != '':
        hotels = hotels.filter(num_people=num_people)

    if price != '💲Price per Night' and price != '':
        hotels = hotels.filter(price=price)
    
    # Get user collections for the bookmark feature
    user_collections = Collection.objects.filter(creator=request.user)
    
    # Always use librarian base template
    base_template = 'base/librarian_base.html'
    
    return render(request, 'patron/search-page.html', {
        'hotels': hotels,
        'query': query,
        'is_librarian': True,  # Always render as librarian view
        'base_template': base_template,
        'user_collections': user_collections
    })