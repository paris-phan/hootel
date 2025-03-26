from django.urls import path
from . import views

app_name = 'patron'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('librarian-search/', views.librarian_search, name='librarian_search'),
    path('book/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Librarian booking management
    path('manage-bookings/', views.manage_booking_requests, name='manage_booking_requests'),
    path('update-booking/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    
    # Room and hotel management (for librarians only)
    path('manage-hotels/', views.manage_hotels, name='manage_hotels'),  
    path('hotels/<int:hotel_id>/view/', views.view_hotel, name='view_hotel'),
    # Patron-specific hotel view
    path('hotels/<int:hotel_id>/patron-view/', views.patron_view_hotel, name='patron_view_hotel'),
    path('hotels/<int:hotel_id>/rooms/', views.list_hotel_rooms, name='list_hotel_rooms'),
    path('rooms/add/', views.add_room, name='add_room'),
    path('rooms/<int:room_id>/', views.view_room, name='view_room'),
    
    # Collection related URLs
    path('collections/', views.view_collections, name='view_collections'),
    path('collections/<int:collection_id>/', views.view_collection_items, name='view_collection_items'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/request-access/<int:collection_id>/', views.request_collection_access, name='request_collection_access'),
    path('rooms/<int:room_id>/add-to-collection/', views.add_room_to_collection, name='add_room_to_collection'),
    path('collections/<int:collection_id>/remove-room/<int:room_id>/', views.remove_room_from_collection, name='remove_room_from_collection'),
    path('bookings/<int:booking_id>/add-to-collection/', views.add_booking_to_collection, name='add_booking_to_collection'),
    path('collections/<int:collection_id>/remove-booking/<int:booking_id>/', views.remove_booking_from_collection, name='remove_booking_from_collection'),
    
    # Backwards compatibility redirect
    path('my-borrowed-items/', views.my_borrowed_items, name='my_borrowed_items'),
    
    # For librarians only - redirects to proper librarian views
    path('create-hotel/', views.create_hotel, name='create_hotel'),
    path('update-hotel-image/<int:hotel_id>/', views.update_hotel_image, name='update_hotel_image'),
    path('hotels/<int:hotel_id>/update/', views.update_hotel, name='update_hotel'),
    path('hotels/<int:hotel_id>/delete/', views.delete_hotel, name='delete_hotel'),
] 