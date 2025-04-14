from django.shortcuts import render, get_object_or_404
from .models import Item
from collection.models import CollectionItems

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

def booking_view(request, item_title):
    # Get the item by title, returning a 404 if not found
    item = get_object_or_404(Item, title=item_title)
    
    # Render the booking template with the item
    return render(request, 'catalog/booking.html', {'item': item})
