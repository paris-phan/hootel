from django.db import models
from django.conf import settings
from catalog.models import Item

class LoanRequest(models.Model):
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Denied'),
        (3, 'Returned'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    denied_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    reservation_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    class Meta:
        db_table = 'loan_request'  # <--- Custom table name
