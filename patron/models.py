from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

def hotel_image_path(instance, filename):
    # File will be uploaded to hotel_data/hotel_<id>/<filename>
    extension = filename.split('.')[-1]
    new_filename = f"hotel_image.{extension}"
    return f'hotel_data/{instance.name}/{new_filename}'

def room_image_path(instance, filename):
    # File will be uploaded to hotel_data/hotel_<id>/rooms/room_<id>/<filename>
    extension = filename.split('.')[-1]
    new_filename = f"room_image.{extension}"
    return f'hotel_data/{instance.hotel.name}/rooms/{instance.number}/{new_filename}'

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=hotel_image_path, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_hotels')

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        """Return the hotel image URL or the default if none exists"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            # Return path to default hotel image in S3 bucket
            return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/hotel_data/default/default_hotel.png"

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    number = models.CharField(max_length=20)
    type = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to=room_image_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.hotel.name} - Room {self.number}"
    
    @property
    def image_url(self):
        """Return the room image URL or the default if none exists"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            # Return path to default room image in S3 bucket
            return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/hotel_data/default/default_room.png"
    
    class Meta:
        unique_together = ('hotel', 'number')

class HotelBooking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"
    
    def get_status_display(self):
        """Return the human-readable status name."""
        if not self.status:
            return "Saved"
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

class Collection(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def can_be_private(self):
        """Only librarians can create private collections."""
        try:
            return self.creator.userprofile.user_type == 'LIBRARIAN'
        except:
            return False

class CollectionRoom(models.Model):
    """
    Model to represent a room in a collection (essentially a favorite or saved room)
    """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='in_collections')
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.room} in {self.collection.name}"
    
    class Meta:
        unique_together = ('collection', 'room')

class CollectionBooking(models.Model):
    """
    Model to represent a hotel booking in a collection (allows patrons to organize their bookings)
    """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='bookings')
    booking = models.ForeignKey(HotelBooking, on_delete=models.CASCADE, related_name='in_collections')
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.booking.hotel.name} booking in {self.collection.name}"
    
    class Meta:
        unique_together = ('collection', 'booking')

# Keeping Item model for backward compatibility but marking it as deprecated
class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    # Add a room field to link to the new Room model
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='legacy_items')
    
    def __str__(self):
        return self.title

class Borrowing(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='borrowings')
    request_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"{self.user.username} - {self.item.title}"
    
    def get_status_display(self):
        """Return the human-readable status name."""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

class CollectionAccessRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_requests')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"{self.user.username} - {self.collection.name}"
    
    def get_status_display(self):
        """Return the human-readable status name."""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
