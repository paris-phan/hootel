from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_access_request, name="create_access_request"),
    path(
        "approve/<int:request_id>/",
        views.approve_access_request,
        name="approve_access_request",
    ),
    path(
        "deny/<int:request_id>/", views.deny_access_request, name="deny_access_request"
    ),
]
