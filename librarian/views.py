from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
# Create your views here.

from django.contrib.auth.decorators import login_required
from hotelmanager6000.models import Hotel
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from patron.models import Hotel as PatronHotel, HotelBooking, Collection, Item, CollectionAccessRequest, CollectionBooking
from django.db.models import Q
from django.db import models

@login_required
def create_hotel(request):
    """
    View for creating new hotels. Only librarians can access this.
    """
    if not request.user.is_staff:
        messages.error(request, "Only librarians can create hotels.")
        return redirect('home')
        
    if request.method == "POST":
        name = request.POST.get("name_field")
        location = request.POST.get("location_field")
        description = request.POST.get("description", "")
        price = request.POST.get("price_per_night")
        num_people = request.POST.get("num_people")
        
        if not name or not location:
            messages.error(request, "Name and location are required fields.")
            return render(request, 'librarian/create_hotel.html')
        
        hotel = PatronHotel(
            name=name,
            location=location,
            description=description,
            created_by=request.user,
            price=price,
            num_people=num_people,
        )
        
        # Handle image upload if provided
        if 'hotel_image' in request.FILES:
            hotel.image = request.FILES['hotel_image']
            
        hotel.save()
        messages.success(request, f"Hotel '{name}' created successfully!")
        return redirect('patron:manage_hotels')
        
    return render(request, 'librarian/create_hotel.html')

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