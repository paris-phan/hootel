from django.urls import path
from . import views
app_name = 'patron'

urlpatterns = [
    # Hotel views
    path('hotels/', views.view_hotels, name='view_hotels'),
    path('hotels/<int:hotel_id>/', views.patron_view_hotel, name='patron_view_hotel'),
    path('hotels/<int:hotel_id>/book/', views.book_hotel, name='book_hotel'),
    path('hotels/<int:hotel_id>/add-to-collection/', views.add_hotel_to_collection, name='add_hotel_to_collection'),

    # Rating views
    path('hotel/<int:hotel_id>/add_review/', views.add_review, name='add_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('edit-review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),

    # Booking management
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<int:booking_id>/add-to-collection/', views.add_booking_to_collection, name='add_booking_to_collection'),
    
    # Collection management
    path('collections/', views.view_collections, name='view_collections'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/', views.view_collection_items, name='view_collection_items'),
    path('collections/<int:collection_id>/edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:collection_id>/delete/', views.delete_collection, name='delete_collection'),
    path('collections/<int:collection_id>/request-access/', views.request_collection_access, name='request_collection_access'),
    path('collections/<int:collection_id>/remove-booking/<int:booking_id>/', views.remove_booking_from_collection, name='remove_booking_from_collection'),
    
    # Collection access management
    path('collection-requests/', views.manage_collection_requests, name='manage_collection_requests'),
    path('collection-requests/<int:request_id>/<str:action>/', views.process_access_request, name='process_access_request'),
    path('collections/<int:collection_id>/revoke-access/<int:user_id>/', views.revoke_collection_access, name='revoke_collection_access'),
    
    # Search and browse
    path('search/', views.search, name='search'),
    
    # Hotel management (for librarians only)
    path('manage-hotels/', views.manage_hotels, name='manage_hotels'),
    path('hotels/<int:hotel_id>/update/', views.update_hotel, name='update_hotel'),
    path('hotels/<int:hotel_id>/delete/', views.delete_hotel, name='delete_hotel'),
    path('hotels/<int:hotel_id>/update-image/', views.update_hotel_image, name='update_hotel_image'),
    path('hotels/<int:hotel_id>/view/', views.view_hotel, name='view_hotel'),
    
    # Booking management (for librarians only)
    path('manage-bookings/', views.manage_booking_requests, name='manage_booking_requests'),
    path('bookings/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
] 