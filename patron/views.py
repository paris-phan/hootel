from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Hotel, HotelBooking, Collection, Item, Borrowing, CollectionAccessRequest
from datetime import datetime
from django.utils import timezone
from django.db import models
from django.views.decorators.http import require_POST

# Create your views here.

@login_required
def view_hotels(request):
    # Redirect to the main search page
    return redirect('patron:search')

@login_required
def book_hotel(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        messages.error(request, "Sorry, the requested hotel does not exist.")
        return redirect('patron:search')
    
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        
        booking = HotelBooking.objects.create(
            user=request.user,
            hotel=hotel,
            check_in_date=check_in,
            check_out_date=check_out
        )
        messages.success(request, 'Booking request submitted successfully!')
        return redirect('patron:my_bookings')
        
    return render(request, 'patron/book_hotel.html', {'hotel': hotel})

@login_required
def my_bookings(request):
    all_bookings = HotelBooking.objects.filter(user=request.user).order_by('-created_at')
    
    # Separate bookings by status
    pending_bookings = all_bookings.filter(status='PENDING')
    approved_bookings = all_bookings.filter(status='APPROVED')
    rejected_bookings = all_bookings.filter(status='REJECTED')
    
    return render(request, 'patron/my_bookings.html', {
        'bookings': all_bookings,  # Keep all bookings for backward compatibility
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings
    })

@login_required
def view_collections(request):
    # Get all public collections
    public_collections = Collection.objects.filter(is_private=False)
    
    # Get private collections (just titles)
    private_collections = Collection.objects.filter(is_private=True)
    
    # Get private collections the user has access to
    user_access_requests = CollectionAccessRequest.objects.filter(
        user=request.user, 
        status='APPROVED'
    ).values_list('collection_id', flat=True)
    
    accessible_private_collections = Collection.objects.filter(
        id__in=user_access_requests, 
        is_private=True
    )
    
    context = {
        'public_collections': public_collections,
        'private_collections': private_collections,
        'accessible_private_collections': accessible_private_collections
    }
    
    return render(request, 'patron/view_collections.html', context)

@login_required
def view_collection_items(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if user can access this collection
    can_access = False
    
    # If it's public, allow access
    if not collection.is_private:
        can_access = True
    # If it's private, check for approved access
    elif CollectionAccessRequest.objects.filter(
        user=request.user, 
        collection=collection,
        status='APPROVED'
    ).exists():
        can_access = True
    # If user is the creator, allow access
    elif collection.creator == request.user:
        can_access = True
        
    if not can_access:
        messages.error(request, "You don't have permission to view this collection.")
        return redirect('patron:view_collections')
        
    items = Item.objects.filter(collection=collection)
    
    return render(request, 'patron/view_collection_items.html', {
        'collection': collection,
        'items': items
    })

@login_required
def request_collection_access(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if request already exists
    existing_request = CollectionAccessRequest.objects.filter(
        user=request.user,
        collection=collection
    ).first()
    
    if existing_request:
        if existing_request.status == 'PENDING':
            messages.info(request, "You've already requested access to this collection.")
        elif existing_request.status == 'APPROVED':
            messages.success(request, "You already have access to this collection.")
        else:
            # If rejected, allow user to request again
            existing_request.status = 'PENDING'
            existing_request.request_date = timezone.now()
            existing_request.save()
            messages.success(request, "Your access request has been resubmitted.")
    else:
        # Create new request
        CollectionAccessRequest.objects.create(
            user=request.user,
            collection=collection
        )
        messages.success(request, "Your request for access has been submitted.")
    
    return redirect('patron:view_collections')

@login_required
def create_collection(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Patrons can only create public collections
        try:
            is_librarian = request.user.userprofile.user_type == 'LIBRARIAN'
        except:
            is_librarian = False
            
        is_private = request.POST.get('is_private') == 'on' and is_librarian
        
        Collection.objects.create(
            name=name,
            description=description,
            creator=request.user,
            is_private=is_private
        )
        
        messages.success(request, "Collection created successfully!")
        return redirect('patron:view_collections')
        
    return render(request, 'patron/create_collection.html')

@login_required
def request_item_borrow(request, item_id):
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
    
    return redirect('patron:view_item', item_id=item.id)

@login_required
def view_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # Check if item is in a private collection
    if item.collection and item.collection.is_private:
        # Check if user can access this collection
        can_access = CollectionAccessRequest.objects.filter(
            user=request.user, 
            collection=item.collection,
            status='APPROVED'
        ).exists() or item.collection.creator == request.user
        
        if not can_access:
            messages.error(request, "You don't have permission to view this item.")
            return redirect('patron:view_collections')
    
    # Get current borrowing status
    borrowing = Borrowing.objects.filter(
        user=request.user,
        item=item
    ).order_by('-request_date').first()
    
    return render(request, 'patron/view_item.html', {
        'item': item,
        'borrowing': borrowing
    })

@login_required
def my_borrowed_items(request):
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
    
    return render(request, 'patron/my_borrowed_items.html', {
        'borrowings': all_borrowings,  # Keep for backward compatibility
        'current_borrowings': current_borrowings,
        'past_borrowings': past_borrowings
    })

def search(request):
    """
    View for the search page where users can search for hotels.
    """
    query = request.GET.get('query', '').strip()
    hotels = Hotel.objects.all()
    
    if query:
        hotels = hotels.filter(Q(name__icontains=query) | Q(location__icontains=query))
    
    # Check if user is a librarian
    is_librarian = False
    if request.user.is_authenticated:
        try:
            is_librarian = request.user.is_staff
        except:
            pass
    
    return render(request, 'patron/search-page.html', {
        'hotels': hotels,
        'query': query,
        'is_librarian': is_librarian
    })

@login_required
def manage_booking_requests(request):
    """
    View for librarians to manage booking requests (approve/decline).
    """
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('home')
    
    # For staff, show all bookings
    if request.user.is_staff:
        pending_bookings = HotelBooking.objects.filter(status='PENDING').order_by('-created_at')
        approved_bookings = HotelBooking.objects.filter(status='APPROVED').order_by('-created_at')
        rejected_bookings = HotelBooking.objects.filter(status='REJECTED').order_by('-created_at')
    else:
        # For regular users, only show bookings for hotels they created
        hotels_created = Hotel.objects.filter(created_by=request.user).values_list('id', flat=True)
        pending_bookings = HotelBooking.objects.filter(hotel_id__in=hotels_created, status='PENDING').order_by('-created_at')
        approved_bookings = HotelBooking.objects.filter(hotel_id__in=hotels_created, status='APPROVED').order_by('-created_at')
        rejected_bookings = HotelBooking.objects.filter(hotel_id__in=hotels_created, status='REJECTED').order_by('-created_at')
    
    return render(request, 'patron/manage_booking_requests.html', {
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings
    })

@login_required
def update_booking_status(request, booking_id, status):
    """
    View to update a booking status (approve/decline).
    """
    booking = get_object_or_404(HotelBooking, id=booking_id)
    
    # Check permissions - must be staff or the hotel creator
    if not request.user.is_staff and booking.hotel.created_by != request.user:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('patron:manage_booking_requests')
    
    if status not in ['APPROVED', 'REJECTED']:
        messages.error(request, "Invalid status.")
        return redirect('patron:manage_booking_requests')
    
    booking.status = status
    booking.save()
    
    status_word = "approved" if status == "APPROVED" else "rejected"
    messages.success(request, f"Booking has been {status_word} successfully.")
    
    return redirect('patron:manage_booking_requests')

@login_required
def create_hotel(request):
    """
    View for creating new hotels.
    """
    if request.method == 'POST':
        name = request.POST.get('name_field')
        location = request.POST.get('location_field')
        description = request.POST.get('description')
        
        if name and location:
            # Create the hotel instance without saving to DB yet
            hotel = Hotel(
                name=name,
                location=location,
                description=description,
                created_by=request.user
            )
            
            # Check if an image was uploaded
            if 'hotel_image' in request.FILES:
                hotel.image = request.FILES['hotel_image']
                
            # Save the hotel to the database
            hotel.save()
            
            messages.success(request, 'Hotel created successfully!')
            return redirect('patron:manage_hotels')
        else:
            messages.error(request, 'Please provide both name and location for the hotel.')
    
    return render(request, 'patron/create_hotel.html')

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
    
    return render(request, 'patron/manage_hotels.html', {
        'hotels': hotels
    })

@login_required
def cancel_booking(request, booking_id):
    """
    View to cancel a booking (for users).
    """
    booking = get_object_or_404(HotelBooking, id=booking_id, user=request.user)
    
    # Only allow cancellation of pending bookings
    if booking.status != 'PENDING':
        messages.error(request, "You can only cancel pending bookings.")
        return redirect('patron:my_bookings')
    
    booking.delete()
    messages.success(request, "Your booking has been cancelled successfully.")
    
    return redirect('patron:my_bookings')

@require_POST
@login_required
def update_hotel_image(request, hotel_id):
    """
    View to update a hotel image.
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Get the hotel
            hotel = get_object_or_404(Hotel, id=hotel_id)
            
            # Check if user has permission (creator or staff)
            if hotel.created_by != request.user and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'You do not have permission to modify this hotel.'
                })
                
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
def view_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    # Get recent bookings (only for staff or hotel creator)
    recent_bookings = []
    if request.user.is_staff or hotel.created_by == request.user:
        recent_bookings = HotelBooking.objects.filter(hotel=hotel).order_by('-created_at')[:10]
    
    return render(request, 'patron/hotel_view.html', {
        'hotel': hotel,
        'recent_bookings': recent_bookings
    })

@login_required
def update_hotel(request, hotel_id):
    """
    View for updating an existing hotel.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    # Check permissions - must be staff or the hotel creator
    if not request.user.is_staff and hotel.created_by != request.user:
        messages.error(request, "You don't have permission to update this hotel.")
        return redirect('patron:manage_hotels')
    
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
    
    return render(request, 'patron/update_hotel.html', {'hotel': hotel})

@login_required
def delete_hotel(request, hotel_id):
    """
    View for deleting a hotel.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    # Check permissions - must be staff or the hotel creator
    if not request.user.is_staff and hotel.created_by != request.user:
        messages.error(request, "You don't have permission to delete this hotel.")
        return redirect('patron:manage_hotels')
    
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
        return redirect('patron:manage_hotels')
    
    return render(request, 'patron/delete_hotel.html', {'hotel': hotel})
