from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Collection, CollectionItems
from catalog.models import Item
from django.db.models import Case, When, Value, IntegerField
from django.http import JsonResponse

# Create your views here.


def collection_list(request):
    collections = Collection.objects.annotate(
        display_order=Case(
            # 1. Public collections with is_region=False
            When(visibility=0, is_region=False, then=Value(1)),
            # 2. Private collections
            When(visibility=1, then=Value(2)),
            # 3. Collections with is_region=True
            When(is_region=True, then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('display_order')

    return render(request, "collections/list.html", {"collections": collections})


def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    # Get IDs of items already in private collections
    items_in_private_collections = CollectionItems.objects.filter(
        collection__visibility=1
    ).values_list("item_id", flat=True)

    # Filter available items to exclude those in private collections
    available_items = Item.objects.exclude(id__in=items_in_private_collections)

    # If this is not a private collection, also exclude items already in this collection
    if collection.visibility == 0:  # Public collection
        already_in_this_collection = CollectionItems.objects.filter(
            collection=collection
        ).values_list("item_id", flat=True)
        available_items = available_items.exclude(id__in=already_in_this_collection)

    is_creator = False
    if request.user.is_authenticated:
        if request.user == collection.creator or request.user.role == 1:
            is_creator = True

    # Check if this is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(
            request,
            "collections/detail.html",
            {
                "collection": collection,
                "available_items": available_items,
                "is_creator": is_creator,
            },
        )

    return render(
        request,
        "collections/detail.html",
        {
            "collection": collection,
            "available_items": available_items,
            "is_creator": is_creator,
        },
    )


@login_required
def create_collection(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        visibility = int(request.POST.get("visibility", 0))

        if not title:
            messages.error(request, "Collection title is required.")
            return redirect("accounts:user_profile", username=request.user.username)

        # Create the collection
        collection = Collection.objects.create(
            title=title,
            description=description,
            creator=request.user,
            visibility=visibility,
        )

        messages.success(
            request,
            f'Collection "{title}" created successfully. You can now add items to it.',
        )
        return redirect("collection:detail", collection_id=collection.id)

    # If not a POST request, redirect to profile
    return redirect("accounts:user_profile", username=request.user.username)


@login_required
def update_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    # Check if user is the creator of the collection or a librarian
    if request.user != collection.creator and request.user.role != 1:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": "You don't have permission to modify this collection.",
                }
            )
        messages.error(request, "You don't have permission to modify this collection.")
        return redirect("collection:detail", collection_id=collection_id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")

        if not title:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "message": "Collection title is required."}
                )
            messages.error(request, "Collection title is required.")
            return redirect("collection:detail", collection_id=collection_id)

        # Update the collection
        collection.title = title
        collection.description = description
        collection.save()

        success_message = f'Collection "{title}" has been updated successfully.'
        messages.success(request, success_message)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": success_message,
                    "collection": {
                        "id": collection.id,
                        "title": collection.title,
                        "description": collection.description,
                        "visibility": collection.visibility,
                        "visibility_display": collection.get_visibility_display(),
                    },
                }
            )

    return redirect("collection:detail", collection_id=collection_id)


@login_required
def remove_item(request, collection_id, item_id):
    collection = get_object_or_404(Collection, id=collection_id)

    # Check if user is the creator of the collection
    if request.user != collection.creator and request.user.role != 1:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": "You don't have permission to modify this collection.",
                }
            )
        messages.error(request, "You don't have permission to modify this collection.")
        return redirect("collection:detail", collection_id=collection_id)

    # Find and delete the collection item
    try:
        collection_item = CollectionItems.objects.get(
            collection=collection, item_id=item_id
        )
        collection_item.delete()
        success_message = "Item removed from collection successfully."
        messages.success(request, success_message)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": success_message})
    except CollectionItems.DoesNotExist:
        error_message = "Item not found in this collection."
        messages.error(request, error_message)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": error_message})

    return redirect("collection:detail", collection_id=collection_id)


@login_required
def add_items(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    #console logs
    print(f"Collection: {collection}")
    print(f"Request: {request}")
    print(f"Using AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
    print(f"User: {request.user}")
    print(f"User Role: {request.user.role}")
    print(f"User is Collection Creator: {request.user == collection.creator}")
    print(f"User is Authenticated: {request.user.is_authenticated}")
    print("Running add_items() in collection/views.py")



    # Check if user is the creator of the collection
    if request.user != collection.creator and request.user.role != 1:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": "You don't have permission to modify this collection.",
                }
            )
        messages.error(request, "You don't have permission to modify this collection.")
        return redirect("collection:detail", collection_id=collection_id)
    
    if request.method == 'POST':
        item_ids = request.POST.getlist('items')
        
        if item_ids:
            # Get existing item IDs in the collection
            existing_item_ids = collection.collectionitems_set.values_list('item_id', flat=True)
            
            # Add only new items to the collection
            items_added = 0
            items_moved = 0
            failed_items = []
            
            #for all items to add
            for item_id in item_ids:

                #if item is not already in the collection
                if int(item_id) not in existing_item_ids:

                    item = get_object_or_404(Item, id=item_id)
                    try:
                        # Try to add the item to the collection
                        CollectionItems.objects.create(collection=collection, item=item)
                        items_added += 1

                    except Exception as e:
                        # If it's a private collection and item is in other collections
                        if collection.visibility == 1:
                            # Find all entries for this item and delete them
                            existing_entries = CollectionItems.objects.filter(item=item)
                            existing_collections = [
                                entry.collection.title for entry in existing_entries
                            ]
                            existing_entries.delete()

                            # Try adding again
                            try:
                                CollectionItems.objects.create(
                                    collection=collection, item=item
                                )
                                items_moved += 1
                            except Exception as e2:
                                # If it still fails, add to failed items
                                failed_items.append((item.title, str(e2)))
                        else:
                            # For other failures, add to failed items
                            failed_items.append((item.title, str(e)))
            
            ##DONE, return messages

            success_message = []
            success_message.append(f"{items_added} items added to the collection\n")
            success_message.append(f"{items_moved} items moved from other collections\n")
            
            num_failed = len(failed_items)
            success_message.append(f"{num_failed} items failed to add\n")

            success_message = ". ".join(success_message) + "."
            
            # Check if this is an AJAX request
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": success_message,
                        "items_added": items_added,
                        "items_moved": items_moved
                    }
                )
            
            # For regular form submission
            messages.success(request, success_message)

    return redirect("collection:detail", collection_id=collection_id)


@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    # Check if user is the creator of the collection or a librarian
    if request.user != collection.creator and request.user.role != 1:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": "You don't have permission to delete this collection.",
                }
            )
        messages.error(request, "You don't have permission to delete this collection.")
        return redirect("collection:detail", collection_id=collection_id)

    if request.method == "POST":
        collection_title = collection.title

        # Delete the collection (this will cascade delete CollectionItems due to FK)
        collection.delete()

        success_message = f'Collection "{collection_title}" has been deleted.'
        messages.success(request, success_message)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": success_message})

        # Redirect to the collections list
        return redirect("collection:list")

    # If not a POST request, redirect back to the collection detail page
    return redirect("collection:detail", collection_id=collection_id)
