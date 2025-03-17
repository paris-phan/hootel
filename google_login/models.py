from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
# user roles

def user_profile_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_data/user_<id>/<filename>
    extension = filename.split('.')[-1]
    new_filename = f"profile_picture.{extension}"
    return f'user_data/{instance.user.email}/{new_filename}'

class UserProfile(models.Model):
    USER_TYPES = (
        ('PATRON', 'Patron'),
        ('LIBRARIAN', 'Librarian'),
    )
    
    profile_picture = models.ImageField(upload_to=user_profile_path, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='PATRON')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    @property
    def profile_picture_url(self):
        """Return the profile picture URL or the default if none exists"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        else:
            # Return path to default image in your S3 bucket
            return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/user_data/default/default_profile.png"
