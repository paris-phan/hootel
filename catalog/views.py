from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Item
from collection.models import CollectionItems
from loans.models import Loan
from datetime import datetime

# Create your views here.

def catalog_list(request):
    items = Item.objects.all().order_by('title')
    return render(request, 'catalog.html', {'items': items})

def item_detail(request, item_title):
    # Get the item by title, returning a 404 if not found
    item = get_object_or_404(Item, title=item_title)
    
    # Get collections this item belongs to
    collection_items = CollectionItems.objects.filter(item=item).select_related('collection')
    is_in_private_collection = any(ci.collection.visibility == 1 for ci in collection_items)
    
    # Render the item detail template with the item and collection info
    return render(request, 'catalog/item_detail.html', {
        'item': item,
        'is_in_private_collection': is_in_private_collection
    })

@login_required
def booking_view(request, item_title):
    item = get_object_or_404(Item, title=item_title)
    
    # Get all approved loans for this item
    existing_loans = Loan.objects.filter(
        item=item,
        status=1  # Approved status
    ).values_list('start_date', 'end_date')
    
    # Convert dates to strings for JavaScript
    disabled_dates = []
    for start_date, end_date in existing_loans:
        if start_date and end_date:
            disabled_dates.append({
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            })
    
    if request.method == 'POST':
        # Get form data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        total_price = request.POST.get('total_price')
        
        # Validate dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Invalid date format')
            return redirect('catalog:booking', item_title=item_title)
        
        # Create new loan
        loan = Loan.objects.create(
            item=item,
            requester=request.user,
            start_date=start_date,
            end_date=end_date,
            reservation_total=total_price,
            status=0  # Pending status
        )
        
        messages.success(request, 'Your booking request has been submitted successfully!')
        return redirect('catalog:item_detail', item_title=item_title)
    
    # Render the booking template with the item and disabled dates
    return render(request, 'catalog/booking.html', {
        'item': item,
        'disabled_dates': disabled_dates
    })
