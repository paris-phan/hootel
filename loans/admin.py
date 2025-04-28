from django.contrib import admin

# Register your models here.
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("item", "requester", "status", "requested_at", "reservation_total")
    list_filter = ("status", "requested_at")
    search_fields = ("item__title", "requester__username")
    readonly_fields = ("requested_at",)
    ordering = ("-requested_at",)
