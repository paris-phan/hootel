from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

def hotel_image_path(instance, filename):
    # File will be uploaded to hotel_data/hotel_<id>/<filename>
    extension = filename.split('.')[-1]
    new_filename = f"hotel_image.{extension}"
    return f'hotel_data/{instance.name}/{new_filename}'

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete = models.CASCADE)
    location = models.CharField(max_length=255)
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=hotel_image_path, null=True, blank=True)

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