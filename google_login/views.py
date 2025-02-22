from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from allauth.socialaccount.models import SocialApp

def home(request):
    if request.user.is_authenticated:

        context = {'name': request.user.username}
        return render(request, "google_login/home.html", context)

    return HttpResponseRedirect('/login')


def login(request):
    if request.user.is_authenticated:
        return redirect('/')

    # Check if Google app is configured
    if not SocialApp.objects.filter(provider='google').exists():
        messages.error(request, 'Google authentication is not configured properly.')
        
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('/')
    else:
        form = AuthenticationForm()

    return render(request, "google_login/login.html", {
        "form": form,
    })

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')