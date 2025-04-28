from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Collection, CollectionItems
from catalog.models import Item
from django.db.models import Case, When, Value, IntegerField

# Create your views here.

def collection_list(request):
    collections = Collection.objects.filter()

    return render(request, 'collections/list.html', {
        'collections': collections
    })

def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    # If the user is the creator, get items that are not already in the collection
    available_items = []
    if request.user == collection.creator or request.user.role == 1:
        # Get IDs of items already in the collection
        existing_item_ids = collection.collectionitems_set.values_list('item_id', flat=True)
        # Get items not in the collection
        available_items = Item.objects.exclude(id__in=existing_item_ids)

    is_creator = False
    if request.user == collection.creator or request.user.role == 1:
        is_creator = True

    return render(request, 'collections/detail.html', {
        'collection': collection,
        'available_items': available_items,
        'is_creator': is_creator
    })

@login_required
def create_collection(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        visibility = int(request.POST.get('visibility', 0))
        item_ids = request.POST.getlist('items')
        
        if not title:
            messages.error(request, 'Collection title is required.')
            return redirect('accounts:user_profile', username=request.user.username)
        
        # Create the collection
        collection = Collection.objects.create(
            title=title,
            description=description,
            creator=request.user,
            visibility=visibility
        )
        
        # Add items to the collection
        if item_ids:
            items = Item.objects.filter(id__in=item_ids)
            for item in items:
                CollectionItems.objects.create(
                    collection=collection,
                    item=item
                )
            messages.success(request, f'Collection "{title}" created with {len(items)} items.')
        else:
            messages.success(request, f'Collection "{title}" created successfully.')
        
        return redirect('collection:detail', collection_id=collection.id)
    
    # If not a POST request, redirect to profile
    return redirect('accounts:user_profile', username=request.user.username)

@login_required
def update_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if user is the creator of the collection or a librarian
    if request.user != collection.creator and request.user.role != 1:
        messages.error(request, "You don't have permission to modify this collection.")
        return redirect('collection:detail', collection_id=collection_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if not title:
            messages.error(request, 'Collection title is required.')
            return redirect('collection:detail', collection_id=collection_id)
        
        # Update the collection
        collection.title = title
        collection.description = description
        collection.save()
        
        messages.success(request, f'Collection "{title}" has been updated successfully.')
    
    return redirect('collection:detail', collection_id=collection_id)

@login_required
def remove_item(request, collection_id, item_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if user is the creator of the collection
    if request.user != collection.creator and request.user.role != 1:
        messages.error(request, "You don't have permission to modify this collection.")
        return redirect('collection:detail', collection_id=collection_id)
    
    # Find and delete the collection item
    try:
        collection_item = CollectionItems.objects.get(collection=collection, item_id=item_id)
        collection_item.delete()
        messages.success(request, "Item removed from collection successfully.")
    except CollectionItems.DoesNotExist:
        messages.error(request, "Item not found in this collection.")
    
    return redirect('collection:detail', collection_id=collection_id)

@login_required
def add_items(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if user is the creator of the collection
    if request.user != collection.creator and request.user.role != 1:
        messages.error(request, "You don't have permission to modify this collection.")
        return redirect('collection:detail', collection_id=collection_id)
    
    if request.method == 'POST':
        item_ids = request.POST.getlist('items')
        
        if item_ids:
            # Get existing item IDs in the collection
            existing_item_ids = collection.collectionitems_set.values_list('item_id', flat=True)
            
            # Add only new items to the collection
            items_added = 0
            for item_id in item_ids:
                if int(item_id) not in existing_item_ids:
                    item = get_object_or_404(Item, id=item_id)
                    CollectionItems.objects.create(
                        collection=collection,
                        item=item
                    )
                    items_added += 1
            
            if items_added > 0:
                messages.success(request, f'{items_added} items added to the collection.')
            else:
                messages.info(request, "No new items were added to the collection.")
        else:
            messages.info(request, "No items were selected.")
    
    return redirect('collection:detail', collection_id=collection_id)

@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    # Check if user is the creator of the collection or a librarian
    if request.user != collection.creator and request.user.role != 1:
        messages.error(request, "You don't have permission to delete this collection.")
        return redirect('collection:detail', collection_id=collection_id)
    
    if request.method == 'POST':
        collection_title = collection.title
        
        # Delete the collection (this will cascade delete CollectionItems due to FK)
        collection.delete()
        
        messages.success(request, f'Collection "{collection_title}" has been deleted.')
        
        # Redirect to the collections list
        return redirect('collection:list')
    
    # If not a POST request, redirect back to the collection detail page
    return redirect('collection:detail', collection_id=collection_id)
