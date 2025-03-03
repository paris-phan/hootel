from django.urls import include, path
from librarian import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('create_hotel/', views.create_hotel, name='create_hotel')
]