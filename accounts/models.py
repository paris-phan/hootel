from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    role = models.IntegerField(
        default=0,
        help_text="0=Patron, 1=Librarian (superusers remain separate)."
    )

    class Meta:
        db_table = 'user'  # <--- Custom table name
