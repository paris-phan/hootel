"""
URL configuration for hotelmanager6000 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def search_redirect(request):
    if hasattr(request.user, 'librarian') and request.user.librarian:
        return redirect('search_rooms')
    return redirect('patron:search')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('google_login.urls')),
    path('patron/', include('patron.urls', namespace='patron')),
    path('', include('librarian.urls')),
    path('search/', search_redirect, name='search'),
]