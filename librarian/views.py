from django.shortcuts import render, redirect
from django.utils import timezone
# Create your views here.

from django.contrib.auth.decorators import login_required
from hotelmanager6000.models import Hotel
def create_hotel(request):
    if request.method == "POST":
        name = request.POST["name_field"]
        location = request.POST["location_field"]
        hotel = Hotel(name = name, owner = request.user, location = location, rating = 0, created_at = timezone.now())
        hotel.save()
        return redirect('/')
    return render(request, 'librarian/create_hotel.html')
@login_required
def librarian_dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'librarian/dashboard.html', context) 