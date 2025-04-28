from django.db import models
from django.conf import settings
from catalog.models import Item


class Loan(models.Model):
    STATUS_CHOICES = (
        (0, "Pending"),
        (1, "Approved"),
        (2, "Denied"),
        (3, "Returned"),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    requested_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reservation_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "loan"  # <--- Custom table name
