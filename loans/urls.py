from django.urls import path
from . import views

app_name = "loans"

urlpatterns = [
    path("booking/<int:loan_id>/cancel/", views.cancel_booking, name="cancel_booking"),
]
