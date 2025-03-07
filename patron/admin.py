from django.contrib import admin
from .models import Hotel, HotelBooking

# Register your models here.
admin.site.register(Hotel)
admin.site.register(HotelBooking)
