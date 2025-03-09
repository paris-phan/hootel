from django.urls import include, path
from librarian import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('create_hotel/', views.create_hotel, name='create_hotel'),
    path('manage_hotels/', views.manage_hotels, name='manage_hotels'),
    path('edit/<int:hotel_id>/', views.edit, name='edit'),
    path('delete/<int:hotel_id>/', views.delete, name='delete')
]