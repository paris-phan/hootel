from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_list, name='list'),
    path('destinations/<str:item_title>/', views.item_detail, name='item_detail'),
] 