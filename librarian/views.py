from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required

@login_required
def librarian_dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'librarian/dashboard.html', context) 