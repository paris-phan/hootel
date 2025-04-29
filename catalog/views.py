from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Item, ItemReview
from .forms import ItemForm
from collection.models import CollectionItems
from loans.models import Loan
from datetime import datetime
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

# Create your views here.


def catalog_list(request):
    items = Item.objects.all().order_by("title")
    return render(request, "catalog.html", {"items": items})


def item_detail(request, item_title):
    # Get the item by title, returning a 404 if not found
    item = get_object_or_404(Item, title=item_title)

    # Get collections this item belongs to
    collection_items = CollectionItems.objects.filter(item=item).select_related(
        "collection"
    )
    is_in_private_collection = any(
        ci.collection.visibility == 1 for ci in collection_items
    )

    # Render the item detail template with the item and collection info
    return render(
        request,
        "catalog/item_detail.html",
        {"item": item, "is_in_private_collection": is_in_private_collection},
    )


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ItemReview, id=review_id)

    # Check if the user is the creator of the review
    if request.user != review.creator:
        messages.error(request, "You do not have permission to delete this review.")
        return redirect("accounts:user_profile", username=request.user.username)

    # Delete the review
    review.delete()
    messages.success(request, "Review deleted successfully.")

    # Redirect back to the user's profile
    return redirect("accounts:user_profile", username=request.user.username)


@login_required
def booking_view(request, item_title):
    item = get_object_or_404(Item, title=item_title)

    # Get all approved loans for this item
    existing_loans = Loan.objects.filter(
        item=item, status=1  # Approved status
    ).values_list("start_date", "end_date")

    # Convert dates to strings for JavaScript
    disabled_dates = []
    for start_date, end_date in existing_loans:
        if start_date and end_date:
            disabled_dates.append(
                {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                }
            )

    if request.method == "POST":
        # Get form data
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        total_price = request.POST.get("total_price")

        # Validate dates
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format")
            return redirect("catalog:booking", item_title=item_title)

        # Create new loan
        loan = Loan.objects.create(
            item=item,
            requester=request.user,
            start_date=start_date,
            end_date=end_date,
            reservation_total=total_price,
            status=0,  # Pending status
        )

        messages.success(
            request, "Your booking request has been submitted successfully!"
        )
        return redirect("catalog:item_detail", item_title=item_title)

    # Render the booking template with the item and disabled dates
    return render(
        request,
        "catalog/booking.html",
        {"item": item, "disabled_dates": disabled_dates},
    )


@login_required
def create_item(request):
    if not request.user.role == 1:  # Check if user is a librarian
        messages.error(request, "You do not have permission to create items.")
        return redirect("core:librarian_dashboard")

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            
            # Process image files before saving
            from PIL import Image
            from io import BytesIO
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import sys
            
            # Process hero_image if present
            if 'hero_image' in request.FILES:
                hero_image = request.FILES['hero_image']
                # Maximum acceptable size for hero image: 600KB
                max_hero_size = 600 * 1024  # 600KB in bytes
                
                # Only resize if file exceeds maximum size
                if hero_image.size > max_hero_size:
                    hero_img = Image.open(hero_image)
                    # Target dimensions for hero image
                    target_width, target_height = 2560, 1080
                    
                    # Calculate new dimensions while maintaining aspect ratio
                    img_ratio = hero_img.width / hero_img.height
                    target_ratio = target_width / target_height
                    
                    if img_ratio > target_ratio:
                        # Image is wider than target ratio, adjust height
                        new_width = target_width
                        new_height = int(target_width / img_ratio)
                    else:
                        # Image is taller than target ratio, adjust width
                        new_height = target_height
                        new_width = int(target_height * img_ratio)
                    
                    # Resize image
                    hero_img = hero_img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Create output buffer
                    output = BytesIO()
                    # Save resized image
                    hero_img.save(output, format='JPEG', quality=90)
                    output.seek(0)
                    
                    # Replace original file with resized version
                    item.hero_image = InMemoryUploadedFile(
                        output, 
                        'ImageField',
                        f"{hero_image.name.split('.')[0]}-reduced.jpg",
                        'image/jpeg',
                        sys.getsizeof(output),
                        None
                    )
            
            # Process representative_image if present
            if 'representative_image' in request.FILES:
                rep_image = request.FILES['representative_image']
                # Maximum acceptable size for representative image: 200KB
                max_rep_size = 400 * 1024  # 200KB in bytes
                
                # Only resize if file exceeds maximum size
                if rep_image.size > max_rep_size:
                    rep_img = Image.open(rep_image)
                    # Target dimensions for representative image
                    target_width, target_height = 800, 600
                    
                    # Calculate new dimensions while maintaining aspect ratio
                    img_ratio = rep_img.width / rep_img.height
                    target_ratio = target_width / target_height
                    
                    if img_ratio > target_ratio:
                        # Image is wider than target ratio, adjust height
                        new_width = target_width
                        new_height = int(target_width / img_ratio)
                    else:
                        # Image is taller than target ratio, adjust width
                        new_height = target_height
                        new_width = int(target_height * img_ratio)
                    
                    # Resize image
                    rep_img = rep_img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Create output buffer
                    output = BytesIO()
                    # Save resized image
                    rep_img.save(output, format='JPEG', quality=85)
                    output.seek(0)
                    
                    # Replace original file with resized version
                    item.representative_image = InMemoryUploadedFile(
                        output, 
                        'ImageField',
                        f"{rep_image.name.split('.')[0]}-reduced.jpg",
                        'image/jpeg',
                        sys.getsizeof(output),
                        None
                    )
            
            item.created_by = request.user
            item.save()
            messages.success(request, "Item created successfully!")
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "message": "Invalid request method"})


@login_required
def update_item(request):
    if not request.user.role == 1:  # Check if user is a librarian
        messages.error(request, "You do not have permission to modify items.")
        return redirect("core:librarian_dashboard")

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found"})

        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "message": "Invalid request method"})


@login_required
def delete_item(request, item_id):
    if not request.user.role == 1:  # Check if user is a librarian
        messages.error(request, "You do not have permission to delete items.")
        return JsonResponse({"success": False, "message": "Permission denied"})

    try:
        item = Item.objects.get(id=item_id)

        # Check if item has any active loans
        active_loans = Loan.objects.filter(
            item=item, status__in=[0, 1]
        )  # Pending or Approved
        if active_loans.exists():
            return JsonResponse(
                {"success": False, "message": "Cannot delete item with active loans."}
            )

        # Delete the item - this will also delete related files due to the signal handler
        item.delete()

        return JsonResponse({"success": True})
    except Item.DoesNotExist:
        return JsonResponse({"success": False, "message": "Item not found"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def add_review(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        # Simple validation
        if not rating or not comment:
            messages.error(request, "Please provide both a rating and comment.")
            return redirect("catalog:item_detail", item_title=item.title)

        # Check if user already has a review for this item
        existing_review = ItemReview.objects.filter(
            item=item, creator=request.user
        ).first()
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Your review has been updated.")
        else:
            # Create new review
            ItemReview.objects.create(
                item=item, creator=request.user, rating=rating, comment=comment
            )
            messages.success(request, "Your review has been submitted.")

        return redirect("catalog:item_detail", item_title=item.title)

    # If not POST, redirect to item detail page
    return redirect("catalog:item_detail", item_title=item.title)
