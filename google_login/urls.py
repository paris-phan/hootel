from django.urls import include, path
from google_login import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
]