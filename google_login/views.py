from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout


def home(request):
    if request.user.is_authenticated:

        context = {'name': request.user.username}
        return render(request, "google_login/home.html", context)

    return HttpResponseRedirect('/login')


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    return render(request, "google_login/login.html")


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')