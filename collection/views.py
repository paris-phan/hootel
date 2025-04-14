from django.shortcuts import render, get_object_or_404
from .models import Collection

# Create your views here.

def collection_list(request):
    collections = Collection.objects.all()
    return render(request, 'collections/list.html', {
        'collections': collections
    })

def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    return render(request, 'collections/detail.html', {
        'collection': collection
    })
