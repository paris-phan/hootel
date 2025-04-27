from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Item, ItemReview
from .forms import ItemForm
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
def delete_review(request, review_id):
    review = get_object_or_404(ItemReview, id=review_id)
    
    # Check if the user is the creator of the review
    if request.user != review.creator:
        messages.error(request, 'You do not have permission to delete this review.')
        return redirect('accounts:user_profile', username=request.user.username)
    
    # Delete the review
    review.delete()
    messages.success(request, 'Review deleted successfully.')
    
    # Redirect back to the user's profile
    return redirect('accounts:user_profile', username=request.user.username)

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

@login_required
def create_item(request):
    if not request.user.role == 1:  # Check if user is a librarian
        messages.error(request, 'You do not have permission to create items.')
        return redirect('core:librarian_dashboard')
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            messages.success(request, 'Item created successfully!')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def update_item(request):
    if not request.user.role == 1:  # Check if user is a librarian
        messages.error(request, 'You do not have permission to modify items.')
        return redirect('core:librarian_dashboard')
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Item not found'
            })
        
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def delete_item(request, item_id):
    if not request.user.role == 1:  # Check if user is a librarian
        messages.error(request, 'You do not have permission to delete items.')
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        })
    
    try:
        item = Item.objects.get(id=item_id)
        
        # Check if item has any active loans
        active_loans = Loan.objects.filter(item=item, status__in=[0, 1])  # Pending or Approved
        if active_loans.exists():
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete item with active loans.'
            })
        
        # Delete the item - this will also delete related files due to the signal handler
        item.delete()
        
        return JsonResponse({
            'success': True
        })
    except Item.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Item not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
