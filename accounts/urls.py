from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/update-photo/', views.update_profile_photo, name='update_profile_photo'),
    path('<str:username>/', views.user_profile, name='user_profile'),
    path('toggle-role/<int:user_id>/', views.toggle_user_role, name='toggle_user_role'),
] 