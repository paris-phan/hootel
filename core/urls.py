from django.urls import path, include
from . import views 

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations/', views.destinations, name='destinations'),
    path('experiences/', views.experiences, name='experiences'),
    path('about/', views.about, name='about'),
    path('accounts/', include('accounts.urls')),
    path('librarian-dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
] 