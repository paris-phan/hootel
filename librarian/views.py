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

def manage_hotels(request):
    hotels = Hotel.objects.all()
    hotels = hotels.filter(owner=request.user.id)
    return render(request, 'librarian/manage_hotels.html', {'hotels': hotels})

def edit(request, hotel_id):
    hotel = Hotel.objects.get(pk = hotel_id)
    if request.method == "POST":
        if request.POST["name_field"] != "":
            hotel.name = request.POST["name_field"]
        if request.POST["location_field"] != "":
            hotel.location = request.POST["location_field"]
        hotel.save()
        return update(request)
    return render(request, 'librarian/edit_hotel.html', {'hotel': hotel})

def delete(request, hotel_id):
    hotel = Hotel.objects.get(pk = hotel_id)
    hotel.delete()
    return update(request)

def update(request):
    hotels = Hotel.objects.all()
    hotels = hotels.filter(owner=request.user.id)
    return render(request, 'librarian/manage_hotels.html', {'hotels': hotels})

@login_required
def librarian_dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'librarian/dashboard.html', context) 