from django.db import models
from django.conf import settings  # for referencing the AUTH_USER_MODEL
from django.core.files.storage import default_storage
from django.db.models.signals import pre_delete
from django.dispatch import receiver

def item_image_path(instance, filename):
    # Create the path: items/<item_title>/<filename>
    return f'items/{instance.title}/{filename}'

class Item(models.Model):
    STATUS_CHOICES = (
        (0, 'Available'),
        (1, 'Reserved'),
        (2, 'Maintenance'),
    )
    title = models.CharField(max_length=255, unique=True)
    identifier = models.CharField(max_length=50, unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    representative_image = models.ImageField(
        upload_to=item_image_path,
        blank=True,
        null=True,
        storage=default_storage,
        help_text="The thumbnail image for the item"
    )
    hero_image = models.ImageField(
        upload_to=item_image_path,
        blank=True,
        null=True,
        storage=default_storage,
        help_text="The main banner image for the item"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # If you want to track who created the item:
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_created'
    )

    def __str__(self):
        return f"{self.title} ({self.identifier})"

    def delete(self, *args, **kwargs):
        # Delete the images from S3 before deleting the item
        if self.representative_image:
            self.representative_image.delete(save=False)
        if self.hero_image:
            self.hero_image.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'item'  # <--- Custom table name

@receiver(pre_delete, sender=Item)
def delete_item_images(sender, instance, **kwargs):
    # This signal handler ensures images are deleted even if the delete() method is bypassed
    if instance.representative_image:
        instance.representative_image.delete(save=False)
    if instance.hero_image:
        instance.hero_image.delete(save=False)

class ItemReview(models.Model):
    # If you want separate reviews/ratings for Items
    rating = models.IntegerField()  # e.g. 1–5
    comment = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'item_review'  # <--- Custom table name
