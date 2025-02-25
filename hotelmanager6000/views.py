from django.shortcuts import render
from .models import Hotel

def search(request):
    query = request.GET.get('query', '').strip()
    hotels = Hotel.objects.all()

    if query:
        hotels = hotels.filter(name__icontains=query) | hotels.filter(location__icontains=query)

    return render(request, 'search-page.html', {'hotels': hotels, 'query': query})
