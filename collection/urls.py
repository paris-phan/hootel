from django.urls import path
from . import views

app_name = 'collection'

urlpatterns = [
    path('', views.collection_list, name='list'),
    path('<int:collection_id>/', views.collection_detail, name='detail'),
] 