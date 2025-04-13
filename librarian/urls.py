from django.urls import include, path
from librarian import views
from patron import views as patron_views

urlpatterns = [
    path('create_hotel/', views.create_hotel, name='create_hotel'),
    path('manage_hotels/', views.manage_hotels, name='manage_hotels'),
    path('update-hotel-image/<int:hotel_id>/', views.update_hotel_image, name='update_hotel_image'),
    path('hotels/<int:hotel_id>/view/', patron_views.view_hotel, name='view_hotel'),
    path('hotels/<int:hotel_id>/update/', views.update_hotel, name='update_hotel'),
    path('hotels/<int:hotel_id>/delete/', views.delete_hotel, name='delete_hotel'),
    path('librarian-search-rooms/', views.search_rooms, name='search_rooms'),
]