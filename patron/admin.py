from django.contrib import admin
from .models import Hotel, HotelBooking, Collection, Item, CollectionAccessRequest, CollectionBooking

# Register your models here.
admin.site.register(Hotel)
admin.site.register(HotelBooking)
admin.site.register(Collection)
admin.site.register(CollectionBooking)
admin.site.register(Item)
admin.site.register(CollectionAccessRequest)
