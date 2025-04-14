from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class AccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    
    # The user requesting access
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='access_requests'
    )
    
    # The collection being requested
    collection = models.ForeignKey(
        'collection.Collection',  # Updated to use the correct app name
        on_delete=models.CASCADE,
        related_name='access_requests'
    )
    
    # Request details
    request_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(help_text="Why the patron is requesting access to this collection")
    
    # Status tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Review details
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Access request by {self.user} for {self.collection}"
    
    def approve(self, reviewer):
        """Approve this access request"""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.review_date = timezone.now()
        self.save()
    
    def deny(self, reviewer, notes=''):
        """Deny this access request"""
        self.status = 'denied'
        self.reviewed_by = reviewer
        self.review_date = timezone.now()
        self.review_notes = notes
        self.save()
