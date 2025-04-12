from django.db import models
from django.conf import settings
from catalog.models import Item

class Collection(models.Model):
    VISIBILITY_CHOICES = (
        (0, 'Public'),
        (1, 'Private'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections_created'
    )
    visibility = models.IntegerField(choices=VISIBILITY_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collection'  # <--- Custom table name

class CollectionItems(models.Model):
    # The many-to-many “through” table linking Collections to Items
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        db_table = 'collection_items'  # <--- Custom table name

class CollectionAuthorizedUser(models.Model):
    # Tracks which users are authorized to see a private collection
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'collection_authorized_user'  # <--- Custom table name
