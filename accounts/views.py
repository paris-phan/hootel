from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Create your views here.

@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
        'role_display': 'Patron' if user.role == 0 else 'Librarian'
    }
    return render(request, 'accounts/profile.html', context)
