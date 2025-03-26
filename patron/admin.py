from django.contrib import admin
from .models import Hotel, HotelBooking, Room, Collection, CollectionRoom, Item, Borrowing, CollectionAccessRequest, CollectionBooking

# Register your models here.
admin.site.register(Hotel)
admin.site.register(HotelBooking)
admin.site.register(Room)
admin.site.register(Collection)
admin.site.register(CollectionRoom)
admin.site.register(CollectionBooking)
admin.site.register(Item)
admin.site.register(Borrowing)
admin.site.register(CollectionAccessRequest)
