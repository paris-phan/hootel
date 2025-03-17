from django.shortcuts import render
from .models import Hotel

def search(request):
    query = request.GET.get('query', '').strip()
    hotels = Hotel.objects.all()

    if query:
        hotels = hotels.filter(name__icontains=query) | hotels.filter(location__icontains=query)
    
    # Check if user is a librarian
    is_librarian = False
    if request.user.is_authenticated:
        try:
            is_librarian = request.user.userprofile.user_type == 'LIBRARIAN'
        except:
            pass

    return render(request, 'search-page.html', {
        'hotels': hotels, 
        'query': query,
        'is_librarian': is_librarian
    })
