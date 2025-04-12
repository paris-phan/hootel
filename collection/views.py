from django.shortcuts import render
from .models import Collection

# Create your views here.

def collection_list(request):
    collections = Collection.objects.all()
    return render(request, 'collections/list.html', {
        'collections': collections
    })
