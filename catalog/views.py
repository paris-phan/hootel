from django.shortcuts import render
from .models import Item

# Create your views here.

def catalog_list(request):
    items = Item.objects.all().order_by('title')
    return render(request, 'catalog.html', {'items': items})
