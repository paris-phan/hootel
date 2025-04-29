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
import os
import random
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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
                
                # Generate random 3-digit number for filename
                random_suffix = f"{random.randint(100, 999)}"
                
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
                        f"{hero_image.name.split('.')[0]}-{random_suffix}.jpg",
                        'image/jpeg',
                        sys.getsizeof(output),
                        None
                    )
                else:
                    # If no resizing needed, still add random suffix to filename
                    name_parts = os.path.splitext(hero_image.name)
                    hero_image.name = f"{name_parts[0]}-{random_suffix}{name_parts[1]}"
            
            # Process representative_image if present
            if 'representative_image' in request.FILES:
                rep_image = request.FILES['representative_image']
                # Maximum acceptable size for representative image: 200KB
                max_rep_size = 400 * 1024  # 200KB in bytes
                
                # Generate random 3-digit number for filename
                random_suffix = f"{random.randint(100, 999)}"
                
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
                        f"{rep_image.name.split('.')[0]}-{random_suffix}.jpg",
                        'image/jpeg',
                        sys.getsizeof(output),
                        None
                    )
                else:
                    # If no resizing needed, still add random suffix to filename
                    name_parts = os.path.splitext(rep_image.name)
                    rep_image.name = f"{name_parts[0]}-{random_suffix}{name_parts[1]}"
            
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
            old_title = item.title
            old_hero_image_path = item.hero_image.name if item.hero_image else None
            old_rep_image_path = item.representative_image.name if item.representative_image else None
            
            form = ItemForm(request.POST, request.FILES, instance=item)
            if form.is_valid():
                updated_item = form.save(commit=False)
                
                # Process images if they're uploaded
                from PIL import Image
                from io import BytesIO
                from django.core.files.uploadedfile import InMemoryUploadedFile
                import sys
                
                # Process hero_image if new one is uploaded
                if 'hero_image' in request.FILES:
                    # Delete old hero image from storage if it exists
                    if old_hero_image_path and default_storage.exists(old_hero_image_path):
                        default_storage.delete(old_hero_image_path)
                        
                    hero_image = request.FILES['hero_image']
                    # Maximum acceptable size for hero image: 600KB
                    max_hero_size = 600 * 1024  # 600KB in bytes
                    
                    # Generate random 3-digit number for filename
                    random_suffix = f"{random.randint(100, 999)}"
                    
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
                        updated_item.hero_image = InMemoryUploadedFile(
                            output, 
                            'ImageField',
                            f"{hero_image.name.split('.')[0]}-{random_suffix}.jpg",
                            'image/jpeg',
                            sys.getsizeof(output),
                            None
                        )
                    else:
                        # If no resizing needed, still add random suffix to filename
                        name_parts = os.path.splitext(hero_image.name)
                        hero_image.name = f"{name_parts[0]}-{random_suffix}{name_parts[1]}"
                
                # Process representative_image if new one is uploaded
                if 'representative_image' in request.FILES:
                    # Delete old representative image from storage if it exists
                    if old_rep_image_path and default_storage.exists(old_rep_image_path):
                        default_storage.delete(old_rep_image_path)
                        
                    rep_image = request.FILES['representative_image']
                    # Maximum acceptable size for representative image: 400KB
                    max_rep_size = 400 * 1024  # 400KB in bytes
                    
                    # Generate random 3-digit number for filename
                    random_suffix = f"{random.randint(100, 999)}"
                    
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
                        updated_item.representative_image = InMemoryUploadedFile(
                            output, 
                            'ImageField',
                            f"{rep_image.name.split('.')[0]}-{random_suffix}.jpg",
                            'image/jpeg',
                            sys.getsizeof(output),
                            None
                        )
                    else:
                        # If no resizing needed, still add random suffix to filename
                        name_parts = os.path.splitext(rep_image.name)
                        rep_image.name = f"{name_parts[0]}-{random_suffix}{name_parts[1]}"
                
                # Save the item first to get the new file paths
                updated_item.save()
                
                # Handle title change - need to update file paths if title changed
                if old_title != updated_item.title and (old_hero_image_path or old_rep_image_path):
                    # Helper function to copy file to new path
                    def copy_file_to_new_path(old_path, new_path):
                        if old_path and default_storage.exists(old_path):
                            # Read the old file
                            file_content = default_storage.open(old_path).read()
                            # Save to new path
                            default_storage.save(new_path, ContentFile(file_content))
                            # Delete the old file
                            default_storage.delete(old_path)
                    
                    # Handle hero image
                    if old_hero_image_path and updated_item.hero_image:
                        # New path would already be correct in updated_item.hero_image.name
                        # Only need to copy if we didn't upload a new image
                        if 'hero_image' not in request.FILES:
                            old_filename = os.path.basename(old_hero_image_path)
                            new_path = f"items/{updated_item.title}/{old_filename}"
                            copy_file_to_new_path(old_hero_image_path, new_path)
                            # Update the path in the model
                            updated_item.hero_image.name = new_path
                    
                    # Handle representative image
                    if old_rep_image_path and updated_item.representative_image:
                        # Only need to copy if we didn't upload a new image
                        if 'representative_image' not in request.FILES:
                            old_filename = os.path.basename(old_rep_image_path)
                            new_path = f"items/{updated_item.title}/{old_filename}"
                            copy_file_to_new_path(old_rep_image_path, new_path)
                            # Update the path in the model
                            updated_item.representative_image.name = new_path
                    
                    # Save again to update file paths
                    updated_item.save()
                
                messages.success(request, "Item updated successfully!")
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors})
        except Item.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found"})

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
