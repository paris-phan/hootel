from django.contrib import admin
from .models import Collection, CollectionItems, CollectionAuthorizedUser


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "creator",
        "visibility",
        "is_region",
        "created_at",
        "updated_at",
    )
    list_filter = ("visibility", "created_at")
    search_fields = ("title", "description", "creator__username")
    date_hierarchy = "created_at"


@admin.register(CollectionItems)
class CollectionItemsAdmin(admin.ModelAdmin):
    list_display = ("collection", "item")
    list_filter = ("collection",)
    search_fields = ("collection__title", "item__title")


@admin.register(CollectionAuthorizedUser)
class CollectionAuthorizedUserAdmin(admin.ModelAdmin):
    list_display = ("collection", "user")
    list_filter = ("collection",)
    search_fields = ("collection__title", "user__username")
