from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Hotel, HotelBooking
from datetime import datetime

# Create your views here.

@login_required
def view_hotels(request):
    hotels = Hotel.objects.all().order_by('-created_at')
    return render(request, 'patron/view_hotels.html', {'hotels': hotels})

@login_required
def book_hotel(request, hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        
        booking = HotelBooking.objects.create(
            user=request.user,
            hotel=hotel,
            check_in_date=check_in,
            check_out_date=check_out
        )
        messages.success(request, 'Booking request submitted successfully!')
        return redirect('my_bookings')
        
    return render(request, 'patron/book_hotel.html', {'hotel': hotel})

@login_required
def my_bookings(request):
    bookings = HotelBooking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'patron/my_bookings.html', {'bookings': bookings})
