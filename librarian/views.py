from django.shortcuts import render, redirect
from django.utils import timezone
# Create your views here.

from django.contrib.auth.decorators import login_required
from hotelmanager6000.models import Hotel
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def create_hotel(request):
    if request.method == "POST":
        name = request.POST["name_field"]
        location = request.POST["location_field"]
        
        hotel = Hotel(
            name=name, 
            owner=request.user, 
            location=location, 
            rating=0, 
            created_at=timezone.now()
        )
        
        # Handle image upload if provided
        if 'hotel_image' in request.FILES:
            hotel.image = request.FILES['hotel_image']
            
        hotel.save()
        return redirect('/')
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