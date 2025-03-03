from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required

def create_hotel(request):
    return render(request, 'librarian/create_hotel.html')
@login_required
def librarian_dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'librarian/dashboard.html', context) 