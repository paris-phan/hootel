from django.db import models
from django.conf import settings  # for referencing the AUTH_USER_MODEL

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
    representative_image = models.ImageField(upload_to='items/', blank=True, null=True)
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

    class Meta:
        db_table = 'item'  # <--- Custom table name

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
