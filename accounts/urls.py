from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/update-photo/', views.update_profile_photo, name='update_profile_photo'),
] 