from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# user roles


class UserProfile(models.Model):
    USER_TYPES = (
        ('PATRON', 'Patron'),
        ('LIBRARIAN', 'Librarian'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='PATRON')

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
