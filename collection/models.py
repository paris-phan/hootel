from django.db import models
from django.conf import settings
from catalog.models import Item

class Collection(models.Model):

    #type definitions
    VISIBILITY_CHOICES = (
        (0, 'Public'),
        (1, 'Private'),
    )


    #parameters
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creator = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections_created')
    visibility = models.IntegerField(choices=VISIBILITY_CHOICES, default=0)
    is_region = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    #validation
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Only check when changing visibility to private
        if self.visibility == 1 and self.pk is not None:  # For existing collections being changed to private
            # Get all items in this collection
            collection_items = CollectionItems.objects.filter(collection=self)
            for item in [ci.item for ci in collection_items]:
                # Check if any item is in other collections
                if CollectionItems.objects.filter(item=item).exclude(collection=self).exists():
                    raise ValidationError(f"Item '{item.title}' is in multiple collections and cannot be in a private collection.")
    
    #save override
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'collection'  # <--- Custom table name



# many-to-many "through" table linking Collections to Items
class CollectionItems(models.Model):

    #parameters
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    #validation
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Check if this item is being added to a private collection
        if self.collection.visibility == 1:  # Private
            # Check if this item exists in any other collection
            other_collections = CollectionItems.objects.filter(item=self.item).exclude(collection=self.collection)
            if other_collections.exists():
                raise ValidationError("This item already exists in another collection and cannot be added to a private collection.")
        
        # Check if this item is already in a private collection
        private_collections = CollectionItems.objects.filter(
            item=self.item,
            collection__visibility=1  # Private
        ).exclude(collection=self.collection)
        
        if private_collections.exists():
            raise ValidationError("This item is already in a private collection and cannot be added to another collection.")

    #save override
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    #table name
    class Meta:
        db_table = 'collection_items'


# Tracks which users are authorized to see a private collection
class CollectionAuthorizedUser(models.Model):
    
    #parameters
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    #table name
    class Meta:
        db_table = 'collection_authorized_users'