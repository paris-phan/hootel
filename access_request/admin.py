from django.contrib import admin
from .models import AccessRequest

@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'collection', 'status', 'request_date', 'reviewed_by', 'review_date')
    list_filter = ('status', 'request_date', 'review_date')
    search_fields = ('user__username', 'collection__name', 'reason', 'review_notes')
    readonly_fields = ('request_date',)
    
    fieldsets = (
        ('Request Details', {
            'fields': ('user', 'collection', 'reason', 'request_date')
        }),
        ('Review Information', {
            'fields': ('status', 'reviewed_by', 'review_date', 'review_notes')
        }),
    )
