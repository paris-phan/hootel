from django.urls import path
from . import views

app_name = 'patron'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('hotels/', views.view_hotels, name='view_hotels'),
    path('book/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Librarian booking management
    path('manage-bookings/', views.manage_booking_requests, name='manage_booking_requests'),
    path('update-booking/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    
    # Hotel management (for librarians)
    path('manage-hotels/', views.manage_hotels, name='manage_hotels'),
    path('create-hotel/', views.create_hotel, name='create_hotel'),
    path('update-hotel-image/<int:hotel_id>/', views.update_hotel_image, name='update_hotel_image'),
    path('hotels/<int:hotel_id>/view/', views.view_hotel, name='view_hotel'),
    path('hotels/<int:hotel_id>/update/', views.update_hotel, name='update_hotel'),
    path('hotels/<int:hotel_id>/delete/', views.delete_hotel, name='delete_hotel'),
    
    # Collection related URLs
    path('collections/', views.view_collections, name='view_collections'),
    path('collections/<int:collection_id>/', views.view_collection_items, name='view_collection_items'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/request-access/<int:collection_id>/', views.request_collection_access, name='request_collection_access'),
    
    # Item related URLs
    path('items/<int:item_id>/', views.view_item, name='view_item'),
    path('items/borrow/<int:item_id>/', views.request_item_borrow, name='request_item_borrow'),
    path('my-borrowed-items/', views.my_borrowed_items, name='my_borrowed_items'),
] 