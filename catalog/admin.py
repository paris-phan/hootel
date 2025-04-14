from django.contrib import admin
from .models import Item, ItemReview

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'identifier', 'status', 'location', 'created_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'identifier', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'identifier', 'status', 'location')
        }),
        ('Details', {
            'fields': ('description', 'representative_image', 'hero_image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )

@admin.register(ItemReview)
class ItemReviewAdmin(admin.ModelAdmin):
    list_display = ('item', 'rating', 'creator', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'item__title')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Review Details', {
            'fields': ('item', 'rating', 'comment', 'creator')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
