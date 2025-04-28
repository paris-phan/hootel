from django.urls import path, include
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("destinations/", views.destinations, name="destinations"),
    path("experiences/", views.experiences, name="experiences"),
    path("about/team/", views.about, name="about"),
    path("about/sources/", views.sources, name="sources"),
    path("accounts/", include("accounts.urls")),
    path("librarian-dashboard/", views.librarian_dashboard, name="librarian_dashboard"),
    path(
        "access-request/<str:action>/<int:request_id>/",
        views.handle_access_request,
        name="handle_access_request",
    ),
    path(
        "loan/<str:action>/<int:loan_id>/",
        views.handle_loan_action,
        name="handle_loan_action",
    ),
    path(
        "revoke-access/<int:auth_id>/",
        views.revoke_collection_access,
        name="revoke_collection_access",
    ),
]
