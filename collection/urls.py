from django.urls import path
from . import views

app_name = "collection"

urlpatterns = [
    path("", views.collection_list, name="list"),
    path("<int:collection_id>/", views.collection_detail, name="detail"),
    path("create/", views.create_collection, name="create"),
    path(
        "<int:collection_id>/remove-item/<int:item_id>/",
        views.remove_item,
        name="remove_item",
    ),
    path("<int:collection_id>/add-items/", views.add_items, name="add_items"),
    path("<int:collection_id>/delete/", views.delete_collection, name="delete"),
    path("<int:collection_id>/update/", views.update_collection, name="update"),
]
