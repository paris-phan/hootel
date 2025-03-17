from django.urls import include, path
from librarian import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('create_hotel/', views.create_hotel, name='create_hotel'),
    path('update_hotel_image/<int:hotel_id>/', views.update_hotel_image, name='update_hotel_image'),
]