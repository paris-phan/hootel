from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

def hotel_image_path(instance, filename):
    # File will be uploaded to hotel_data/hotel_<id>/<filename>
    extension = filename.split('.')[-1]
    new_filename = f"hotel_image.{extension}"
    return f'hotel_data/{instance.name}/{new_filename}'

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    num_people = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
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

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Ensure that this field only accepts valid ratings (1-5)
    comment = models.TextField(blank=True, null=True)  # Allow comments to be optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.hotel.name} - Rating: {self.rating}"
class Collection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name

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

class CollectionAccessRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} requests access to {self.collection.name}"
    
    class Meta:
        unique_together = ('collection', 'user')

# Keeping Item model for backward compatibility but marking it as deprecated
class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
