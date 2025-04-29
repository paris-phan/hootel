from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from catalog.models import Item
from collection.models import Collection, CollectionItems, CollectionAuthorizedUser
from access_request.models import AccessRequest
from django.contrib.auth import get_user_model
import json
from loans.models import Loan

# Create your views here.


def handler404(request, exception):
    return render(request, "core/404.html", status=404)


def handler500(request):
    return render(request, "core/500.html", status=500)


def home(request):
    """
    Homepage view.
    """
    # Get the first 2 items for featured destinations
    featured_items = Item.objects.all()[:2]

    # Get the next 3 items for experiences
    experience_items = Item.objects.all()[2:5]

    # Format featured destinations
    featured_destinations = []
    for item in featured_items:
        try:
            if item.representative_image and hasattr(item.representative_image, "url"):
                image_path = item.representative_image.url
            else:
                image_path = "core/images/destination-feature.jpg"
        except Exception:
            # In case of any errors with the image, use default
            image_path = "core/images/destination-feature.jpg"

        featured_destinations.append(
            {
                "name": item.title,
                "description": item.description or "",
                "representative_image": image_path,
                "id": item.id,
            }
        )

    # Format experiences
    experiences = []
    for item in experience_items:
        try:
            if item.representative_image and hasattr(item.representative_image, "url"):
                image_path = item.representative_image.url
            else:
                image_path = "core/images/destination-feature.jpg"
        except Exception:
            # In case of any errors with the image, use default
            image_path = "core/images/destination-feature.jpg"

        experiences.append(
            {
                "name": item.title,
                "description": item.description or "",
                "representative_image": image_path,
                "id": item.id,
            }
        )

    context = {
        "page_title": "Tel Resorts, Hotels & Residences – Explore Luxury Destinations",
        "featured_destinations": featured_destinations,
        "experiences": experiences,
    }
    return render(request, "core/home.html", context)


def destinations(request):
    """
    Destinations page view.
    """
    # Get all items from the catalog
    items = Item.objects.all()

    # Get all collections
    collections = Collection.objects.all()

    # Map items to destination format
    destinations = []
    for item in items:
        # Get collections this item belongs to
        item_collections = CollectionItems.objects.filter(item=item).select_related(
            "collection"
        )

        # Check if the item is in any private collections
        is_in_private_collection = any(
            ci.collection.visibility == 1 for ci in item_collections
        )

        # Skip items that are in private collections
        if is_in_private_collection:
            continue

        collection_ids = [ci.collection.id for ci in item_collections]

        # Find the region collection this item belongs to
        region_collection = next(
            (ci.collection for ci in item_collections if ci.collection.is_region), None
        )

        # Set region based on collection, default to 'asia' if no region collection found
        region = region_collection.title.lower() if region_collection else "asia"

        # Handle image - use a safe default
        try:
            if item.representative_image and hasattr(item.representative_image, "url"):
                image_path = item.representative_image.url
            else:
                image_path = "images/default-destination.jpg"
        except Exception:
            # In case of any errors with the image, use default
            image_path = "images/default-destination.jpg"

        destinations.append(
            {
                "name": item.title,
                "description": item.description or "",
                "price": item.price_per_night or 0,
                "representative_image": image_path,
                "region": region,
                "collection_ids": collection_ids,
            }
        )

    context = {
        "page_title": "Destinations | Tel Resorts",
        "destinations": destinations,
        "collections": collections,
    }
    return render(request, "core/destinations.html", context)


def experiences(request):
    """
    Experiences page view.
    """
    # Get all items from the catalog
    items = Item.objects.all()

    # Get all collections
    collections = Collection.objects.all()

    # Add authorization status to collections
    collections_with_auth = []
    for collection in collections:
        is_auth = False
        if request.user.is_authenticated:
            is_auth = CollectionAuthorizedUser.objects.filter(
                collection=collection, user=request.user
            ).exists()

            if request.user.role == 1:
                is_auth = True
        
        # Get authorized users for this collection
        authorized_users = []
        if collection.visibility == 1:  # Private collection
            auth_users = CollectionAuthorizedUser.objects.filter(collection=collection)
            authorized_users = [{'id': au.user.id, 'username': au.user.username} for au in auth_users]

        collections_with_auth.append(
            {
                "id": collection.id,
                "title": collection.title,
                "description": collection.description,
                "visibility": collection.visibility,
                "is_region": collection.is_region,
                "is_authorized": is_auth,
                "authorized_users": authorized_users
            }
        )

    # Map items to destination format
    destinations = []
    for item in items:
        # Get collections this item belongs to
        item_collections = CollectionItems.objects.filter(item=item).select_related(
            "collection"
        )

        # Check if the item is in any private collections
        is_in_private_collection = any(
            ci.collection.visibility == 1 for ci in item_collections
        )

        # Skip items that are not in private collections
        if not is_in_private_collection:
            continue

        collection_ids = [ci.collection.id for ci in item_collections]

        # special to experiences
        #
        # Check if user is authorized for any of the collections
        is_authorized = False
        if request.user.is_authenticated:
            # Check if user is authorized for any of this item's collections
            authorized_collections = CollectionAuthorizedUser.objects.filter(
                collection__id__in=collection_ids, user=request.user
            ).exists()
            is_authorized = authorized_collections
        #
        #
        # end special to experiences

        # Find the region collection this item belongs to
        region_collection = next(
            (ci.collection for ci in item_collections if ci.collection.is_region), None
        )

        # Set region based on collection, default to 'asia' if no region collection found
        region = region_collection.title.lower() if region_collection else "asia"

        # Handle image - use a safe default
        try:
            if item.representative_image and hasattr(item.representative_image, "url"):
                image_path = item.representative_image.url
            else:
                image_path = "images/default-destination.jpg"
        except Exception:
            # In case of any errors with the image, use default
            image_path = "images/default-destination.jpg"

        destinations.append(
            {
                "name": item.title,
                "description": item.description or "",
                "price": item.price_per_night or 0,
                "representative_image": image_path,
                "region": region,
                "collection_ids": collection_ids,
                "has_private_collection": True,  # Since we only include items with private collections
                "is_authorized_for_user": is_authorized,  # Add authorization flag
            }
        )

    context = {
        "page_title": "Experiences | Tel Resorts",
        "destinations": destinations,
        "collections": collections_with_auth,
    }
    return render(request, "core/experiences.html", context)


def about(request):
    """
    About page view.
    """
    context = {
        "page_title": "About Us | Tel Resorts",
    }
    return render(request, "core/about.html", context)


def sources(request):
    """
    Sources page view.
    """
    context = {
        "page_title": "Sources | Tel Resorts",
    }
    return render(request, "core/sources.html", context)


def is_librarian(user):
    return user.is_staff or user.is_superuser or user.role == 1


@login_required
@user_passes_test(is_librarian)
def librarian_dashboard(request):
    """
    Dashboard view for librarians to manage items and collections.
    """
    # Get all items with their details
    items = Item.objects.all().select_related("created_by").prefetch_related("reviews")

    # Get all collections with their items
    collections = (
        Collection.objects.all()
        .select_related("creator")
        .prefetch_related("collectionitems_set__item")
    )

    # Get all access requests
    access_requests = AccessRequest.objects.all().select_related(
        "user", "collection", "reviewed_by"
    )
    
    # Get all collection authorized users
    authorized_users = CollectionAuthorizedUser.objects.all().select_related(
        "user", "collection"
    )

    # Get all users
    users = get_user_model().objects.all().order_by("date_joined")

    # Get all loans
    loans = (
        Loan.objects.all().select_related("item", "requester").order_by("-requested_at")
    )

    context = {
        "page_title": "Librarian Dashboard",
        "items": items,
        "collections": collections,
        "access_requests": access_requests,
        "authorized_users": authorized_users,
        "users": users,
        "loans": loans,
    }
    return render(request, "core/librarian_dashboard.html", context)


@login_required
@user_passes_test(is_librarian)
@require_POST
def handle_access_request(request, action, request_id):
    """Handle access request approval or denial"""
    try:
        access_request = get_object_or_404(AccessRequest, id=request_id)

        if action == "approve":
            # Create CollectionAuthorizedUser entry
            CollectionAuthorizedUser.objects.create(
                collection=access_request.collection, user=access_request.user
            )
            # Delete the access request
            access_request.delete()
            message = "Access request approved successfully"
        elif action == "deny":
            # Just delete the access request
            access_request.delete()
            message = "Access request denied successfully"

        return JsonResponse({"success": True, "message": message})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
@user_passes_test(is_librarian)
@require_POST
def handle_loan_action(request, action, loan_id):
    """Handle loan approval, return, or deletion"""
    try:
        loan = get_object_or_404(Loan, id=loan_id)

        if action == "approve":

            #deny all other loans for this item that overlap in time
            Loan.objects.filter(
                item=loan.item,
                start_date__lte=loan.end_date,
                end_date__gte=loan.start_date
            ).update(status=2)

            loan.status = 1  # Approved
            loan.save()

            message = "Loan approved successfully"

        elif action == "return":
            loan.status = 3  # Returned
            loan.save()
            message = "Item returned successfully"
        elif action == "delete":
            loan.delete()
            message = "Loan deleted successfully"
        elif action == "deny":
            loan.status = 2  # Denied
            loan.save()
            message = "Loan denied successfully"
        else:
            return JsonResponse(
                {"success": False, "message": "Invalid action"}, status=400
            )

        return JsonResponse({"success": True, "message": message})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
@user_passes_test(is_librarian)
@require_POST
def revoke_collection_access(request, auth_id):
    """Revoke a user's access to a collection"""
    try:
        auth_user = get_object_or_404(CollectionAuthorizedUser, id=auth_id)
        auth_user.delete()
        return JsonResponse({"success": True, "message": "Access revoked successfully"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
