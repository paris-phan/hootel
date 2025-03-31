from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.views.decorators.csrf import csrf_exempt

from .models import Hotel, HotelBooking, Collection, Item, CollectionAccessRequest, CollectionBooking, Review
from datetime import datetime
from django.utils import timezone
from django.db import models
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def view_hotels(request):
    """
    Redirects to the search view, where hotels are displayed.
    This maintains backward compatibility with existing URLs.
    """
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
    
    # Add search functionality
    query = request.GET.get('query', '').strip()
    if query:
        all_bookings = all_bookings.filter(
            Q(hotel__name__icontains=query) | 
            Q(hotel__location__icontains=query) |
            Q(check_in_date__icontains=query) |
            Q(check_out_date__icontains=query)
        )
    
    # Separate bookings by status
    pending_bookings = all_bookings.filter(status='PENDING')
    approved_bookings = all_bookings.filter(status='APPROVED')
    rejected_bookings = all_bookings.filter(status='REJECTED')
    
    # Get user collections for the "Add to Collection" feature
    user_collections = Collection.objects.filter(creator=request.user)
    
    return render(request, 'patron/my_bookings.html', {
        'bookings': all_bookings,  # Keep all bookings for backward compatibility
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings,
        'user_collections': user_collections,
        'query': query
    })

@login_required
def view_collections(request):
    # Get all public collections
    public_collections = Collection.objects.filter(is_private=False)
    
    # Get user's own collections (both public and private)
    user_collections = Collection.objects.filter(creator=request.user)
    
    # Get private collections the user has explicit access to through requests
    user_access_requests = CollectionAccessRequest.objects.filter(
        user=request.user, 
        status='APPROVED'
    ).values_list('collection_id', flat=True)
    
    # Combine user's own private collections with those they have explicit access to
    accessible_private_collections = Collection.objects.filter(
        (Q(creator=request.user) | Q(id__in=user_access_requests)) & 
        Q(is_private=True)
    ).distinct()
    
    # Get other private collections (that user doesn't have access to)
    private_collections = Collection.objects.filter(
        is_private=True
    ).exclude(
        id__in=accessible_private_collections.values_list('id', flat=True)
    )
    
    context = {
        'public_collections': public_collections,
        'private_collections': private_collections,
        'accessible_private_collections': accessible_private_collections,
        'user_collections': user_collections,
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
    
    # Get bookings in this collection
    collection_bookings = CollectionBooking.objects.filter(collection=collection).select_related('booking')
    
    # Get users with access (for collection owners)
    users_with_access = []
    if collection.creator == request.user and collection.is_private:
        users_with_access = CollectionAccessRequest.objects.filter(
            collection=collection,
            status='APPROVED'
        ).select_related('user').order_by('user__username')
    
    return render(request, 'patron/view_collection_items.html', {
        'collection': collection,
        'collection_bookings': collection_bookings,
        'users_with_access': users_with_access,
        'is_owner': collection.creator == request.user
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
        
        # Allow any user to set privacy
        is_private = request.POST.get('is_private') == 'on'
        
        collection = Collection.objects.create(
            name=name,
            description=description,
            creator=request.user,
            is_private=is_private
        )
        
        privacy_status = "private" if is_private else "public"
        messages.success(request, f"Collection created successfully! It is {privacy_status}.")
        return redirect('patron:view_collections')
        
    return render(request, 'patron/create_collection.html')

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
    
    return render(request, 'patron/view_item.html', {
        'item': item
    })

def search(request):
    query = request.GET.get('query', '').strip()
    sort_by = request.GET.get('sort_by', '')
    num_people = request.GET.get('num_people', '')
    price = request.GET.get('price_per_night', '')

    hotels = Hotel.objects.annotate(average_rating=Avg('review__rating'))
    for hotel in hotels:
        hotel.average_rating = hotel.review_set.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    if sort_by == 'rating':
        hotels = hotels.order_by('-average_rating', '-created_at')  # Highest rating first
    else:  # Default to alphabetical if 'alphabetical' is selected
        hotels = hotels.order_by('name')

    if num_people != '👥 Travelers' and num_people != '':
        hotels = hotels.filter(num_people=num_people)

    if price != '💲Price per Night' and price != '':
        hotels = hotels.filter(price=price)

    user_collections = []
    if request.user.is_authenticated:
        user_collections = Collection.objects.filter(creator=request.user)

    base_template = 'base/patron_base.html'

    return render(request, 'patron/search-page.html', {
        'hotels': hotels,
        'query': query,
        'is_librarian': False,
        'base_template': base_template,
        'user_collections': user_collections
    })


@login_required
def librarian_search(request):
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
            Q(name__icontains=query) | 
            Q(location__icontains=query) | 
            Q(description__icontains=query)
        )

    if sort_by == 'rating':
        hotels = hotels.order_by('-average_rating', '-created_at')  # Highest rating first
    else:  # Default to alphabetical if 'alphabetical' is selected
        hotels = hotels.order_by('name')

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
        'rejected_bookings': rejected_bookings,
        'base_template': 'base/librarian_base.html'
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
    View for creating new hotels - redirects to the librarian's create_hotel view.
    Regular users should not be able to create hotels.
    """
    # Only librarians can create hotels
    if not request.user.is_staff:
        messages.error(request, "Only librarians can create hotels.")
        return redirect('home')
        
    # Redirect to the librarian's create_hotel view
    return redirect('create_hotel')

@login_required
def manage_hotels(request):
    """
    View for managing hotels.
    """
    # Only staff can access this page
    if not request.user.is_staff:
        messages.error(request, "Only librarians can manage hotels.")
        return redirect('home')
    
    # Show all hotels for staff
    hotels = Hotel.objects.all().order_by('-created_at')
    
    return render(request, 'patron/manage_hotels.html', {
        'hotels': hotels,
        'base_template': 'base/librarian_base.html'
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
    """
    View function for displaying hotel details with librarian features.
    This is the administrative view showing all details and management options.
    """
    # Only staff can access this view
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this view.")
        return redirect('patron:patron_view_hotel', hotel_id=hotel_id)
    
    hotel = get_object_or_404(Hotel, id=hotel_id)
    reviews = hotel.review_set.all()  # Fetching reviews
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Get recent bookings
    recent_bookings = HotelBooking.objects.filter(hotel=hotel).order_by('-created_at')[:10]
    
    return render(request, 'librarian/librarian_hotel_view.html', {
        'hotel': hotel,
        "reviews": reviews,
        "average_rating": average_rating or "N/A",
        'recent_bookings': recent_bookings,
        'base_template': base_template,
        'is_librarian': True  # Always render as librarian view
    })

@login_required
def patron_view_hotel(request, hotel_id):
    """
    View function for displaying hotel details for patrons.
    This view ensures users only see patron-appropriate information,
    using a template that never shows librarian features.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    reviews = hotel.review_set.all()  # Fetching reviews
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Get only the current user's bookings for this hotel
    user_bookings = []
    if request.user.is_authenticated:
        user_bookings = HotelBooking.objects.filter(
            hotel=hotel, 
            user=request.user
        ).order_by('-created_at')
    
    # Always use patron base template for this view
    base_template = 'base/patron_base.html'

    return render(request, "patron/patron_hotel_view.html", {
        "hotel": hotel,
        "reviews": reviews,
        "average_rating": average_rating or "N/A"
    })

@login_required
def add_review(request, hotel_id):
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "")  # Default to empty string if not provided
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return redirect('patron:patron_view_hotel', hotel_id=hotel_id)
            hotel = get_object_or_404(Hotel, id=hotel_id)
            Review.objects.create(user=request.user, hotel=hotel, rating=rating, comment=comment)
            return redirect('patron:patron_view_hotel', hotel_id=hotel.id)
        except (ValueError, TypeError):
            return redirect('patron:patron_view_hotel', hotel_id=hotel_id)

    return redirect('patron:patron_view_hotel', hotel_id=hotel_id)

@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related('hotel').order_by('-created_at')
    return render(request, 'patron/my_reviews.html', {'reviews': reviews})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == "POST":
        # Directly update the review attributes
        review.comment = request.POST.get('comment', review.comment)
        review.rating = request.POST.get('rating', review.rating)
        review.save()
        return redirect('patron:my_reviews')  # Redirect to My Reviews page after saving

    return render(request, 'patron/edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()  # Delete the review
    return redirect('patron:my_reviews')  # Redirect back to My Reviews page

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
        num_people = request.POST.get('num_people')
        price = request.POST.get('price_per_night')
        
        if name and location:
            hotel.name = name
            hotel.location = location
            hotel.description = description
            hotel.price = price
            hotel.num_people = num_people
            
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
    
    return render(request, 'patron/update_hotel.html', {
        'hotel': hotel,
        'base_template': 'base/librarian_base.html'
    })

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
    
    return render(request, 'patron/delete_hotel.html', {
        'hotel': hotel,
        'base_template': 'base/librarian_base.html'
    })

@login_required
def add_booking_to_collection(request, booking_id):
    booking = get_object_or_404(HotelBooking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        collection_id = request.POST.get('collection_id')
        notes = request.POST.get('notes', '')
        
        # Check if collection exists and belongs to the user
        try:
            collection = Collection.objects.get(id=collection_id, creator=request.user)
        except Collection.DoesNotExist:
            messages.error(request, "The selected collection does not exist or you don't have permission to add bookings to it.")
            return redirect('patron:my_bookings')
        
        # Check if booking is already in the collection
        if CollectionBooking.objects.filter(collection=collection, booking=booking).exists():
            messages.info(request, "This booking is already in your collection.")
        else:
            # Add booking to collection
            CollectionBooking.objects.create(
                collection=collection,
                booking=booking,
                notes=notes
            )
            messages.success(request, f"Booking for {booking.hotel.name} added to your collection.")
        
        return redirect('patron:view_collection_items', collection_id=collection.id)
    
    # If GET request, show the form to select a collection
    collections = Collection.objects.filter(creator=request.user)
    
    return render(request, 'patron/add_booking_to_collection.html', {
        'booking': booking,
        'collections': collections
    })

@login_required
def remove_booking_from_collection(request, collection_id, booking_id):
    collection_booking = get_object_or_404(
        CollectionBooking, 
        collection_id=collection_id, 
        booking_id=booking_id,
        collection__creator=request.user
    )
    
    collection_booking.delete()
    messages.success(request, "Booking removed from collection successfully.")
    
    return redirect('patron:view_collection_items', collection_id=collection_id)

@login_required
def add_hotel_to_collection(request, hotel_id):
    """
    View function to add a hotel directly to a collection.
    Creates a booking entry with null status to represent a saved hotel.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        collection_id = request.POST.get('collection_id')
        notes = request.POST.get('notes', '')
        
        # Check if collection exists and belongs to the user
        try:
            collection = Collection.objects.get(id=collection_id, creator=request.user)
        except Collection.DoesNotExist:
            messages.error(request, "The selected collection does not exist or you don't have permission to add hotels to it.")
            return redirect('patron:patron_view_hotel', hotel_id=hotel_id)
        
        # Add the hotel to the collection by creating a booking with null status
        booking, created = HotelBooking.objects.get_or_create(
            user=request.user,
            hotel=hotel,
            status=None,  # Using null status for saved hotels
            check_in_date=None,
            check_out_date=None
        )
        
        # Check if booking is already in the collection
        if CollectionBooking.objects.filter(collection=collection, booking=booking).exists():
            messages.info(request, f"{hotel.name} is already in your collection.")
        else:
            # Add booking to collection
            CollectionBooking.objects.create(
                collection=collection,
                booking=booking,
                notes=notes
            )
            messages.success(request, f"{hotel.name} added to your collection.")
        
        # Return to the search page with the same query
        query = request.GET.get('query', '')
        if query:
            return redirect(f"{reverse('patron:search')}?query={query}")
        return redirect('patron:search')
    
    # If GET request, redirect to view hotel
    return redirect('patron:patron_view_hotel', hotel_id=hotel_id)

@login_required
def edit_collection(request, collection_id):
    """
    View to edit a collection's name, description, and privacy status.
    Only the creator of the collection can edit it and change its privacy status.
    """
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if user is the creator of the collection
    if collection.creator != request.user:
        messages.error(request, "You don't have permission to edit this collection.")
        return redirect('patron:view_collections')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Allow any collection owner to set privacy
        is_private = request.POST.get('is_private') == 'on'
        
        if name:
            collection.name = name
            collection.description = description
            collection.is_private = is_private
            collection.save()
            
            privacy_status = "private" if is_private else "public"
            messages.success(request, f"Collection updated successfully! It is now {privacy_status}.")
            return redirect('patron:view_collection_items', collection_id=collection.id)
        else:
            messages.error(request, "Collection name cannot be empty.")
    
    context = {
        'collection': collection,
        'base_template': 'base/patron_base.html' if not request.user.is_staff else 'base/librarian_base.html'
    }
    return render(request, 'patron/edit_collection.html', context)

@login_required
def delete_collection(request, collection_id):
    """
    View to delete a collection.
    Only the creator of the collection can delete it.
    """
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if user is the creator of the collection
    if collection.creator != request.user:
        messages.error(request, "You don't have permission to delete this collection.")
        return redirect('patron:view_collections')
    
    # If POST request, perform the deletion
    if request.method == 'POST':
        collection_name = collection.name
        collection.delete()
        messages.success(request, f'Collection "{collection_name}" has been deleted successfully.')
        return redirect('patron:view_collections')
    
    # If GET request, show confirmation page
    return render(request, 'patron/delete_collection.html', {
        'collection': collection
    })

@login_required
def manage_collection_requests(request):
    """
    View for users to manage access requests for their private collections.
    Shows all pending requests that other users have made to access the user's collections.
    """
    # Get all collections created by the user
    user_collections = Collection.objects.filter(creator=request.user)
    
    # Get all pending access requests for those collections
    pending_requests = CollectionAccessRequest.objects.filter(
        collection__in=user_collections,
        status='PENDING'
    ).select_related('user', 'collection').order_by('-request_date')
    
    # Get all approved/rejected requests for historical reference
    processed_requests = CollectionAccessRequest.objects.filter(
        collection__in=user_collections,
        status__in=['APPROVED', 'REJECTED']
    ).select_related('user', 'collection').order_by('-request_date')
    
    return render(request, 'patron/manage_collection_requests.html', {
        'pending_requests': pending_requests,
        'processed_requests': processed_requests,
        'base_template': 'base/patron_base.html' if not request.user.is_staff else 'base/librarian_base.html'
    })

@login_required
def process_access_request(request, request_id, action):
    """
    View to approve or reject a collection access request.
    Only the collection creator can approve/reject requests.
    """
    access_request = get_object_or_404(CollectionAccessRequest, id=request_id)
    
    # Verify that the current user is the collection creator
    if access_request.collection.creator != request.user:
        messages.error(request, "You don't have permission to process this request.")
        return redirect('patron:manage_collection_requests')
    
    # Process the request based on the action
    if action == 'approve':
        access_request.status = 'APPROVED'
        access_request.save()
        messages.success(request, f"Access request from {access_request.user.username} has been approved.")
    elif action == 'reject':
        access_request.status = 'REJECTED'
        access_request.save()
        messages.warning(request, f"Access request from {access_request.user.username} has been rejected.")
    else:
        messages.error(request, "Invalid action.")
    
    return redirect('patron:manage_collection_requests')

@login_required
def revoke_collection_access(request, collection_id, user_id):
    """
    View to revoke a user's access to a private collection.
    Only the collection creator can revoke access.
    """
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Verify that the current user is the collection creator
    if collection.creator != request.user:
        messages.error(request, "You don't have permission to manage access to this collection.")
        return redirect('patron:view_collection_items', collection_id=collection.id)
    
    # Find the access request and change its status to REJECTED
    try:
        access_request = CollectionAccessRequest.objects.get(
            collection=collection,
            user_id=user_id,
            status='APPROVED'
        )
        
        user_name = access_request.user.username
        access_request.status = 'REJECTED'
        access_request.save()
        
        messages.success(request, f"Access for {user_name} has been revoked successfully.")
    except CollectionAccessRequest.DoesNotExist:
        messages.error(request, "No active access found for this user.")
    
    return redirect('patron:view_collection_items', collection_id=collection.id)
