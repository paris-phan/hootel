from django.contrib import admin
from .models import Item, ItemReview


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "location",
        "price_per_night",
        "created_at",
        "created_by",
    )
    list_filter = ("status", "created_at")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "status", "location", "price_per_night")},
        ),
        ("Description", {"fields": ("description",)}),
        ("Images", {"fields": ("representative_image", "hero_image")}),
        ("Metadata", {"fields": ("created_by", "created_at")}),
    )


@admin.register(ItemReview)
class ItemReviewAdmin(admin.ModelAdmin):
    list_display = ("item", "rating", "creator", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("comment", "item__title")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Review Details", {"fields": ("item", "rating", "comment", "creator")}),
        ("Metadata", {"fields": ("created_at",)}),
    )
