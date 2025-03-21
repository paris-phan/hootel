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
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"
    
    def get_status_display(self):
        """Return the human-readable status name."""
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

class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    
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
