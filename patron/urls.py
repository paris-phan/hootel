from django.urls import path
from . import views

urlpatterns = [
    path('hotels/', views.view_hotels, name='view_hotels'),
    path('book/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
] 