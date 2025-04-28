from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import default_storage


def user_profile_picture_path(instance, filename):
    # Get the file extension
    ext = filename.split(".")[-1]
    # Create the path: accounts/<username>/<filename>.<ext>
    return f"accounts/{instance.username}/{filename}"


class User(AbstractUser):
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    role = models.IntegerField(
        default=0, help_text="0=Patron, 1=Librarian (superusers remain separate)."
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        null=True,
        blank=True,
        storage=default_storage,
    )

    class Meta:
        db_table = "user"  # <--- Custom table name
