from django.db import connection
from django.shortcuts import render

def search(request):
    query = request.GET.get('query', '').strip()
    hotels = []

    if query:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name, location FROM hotels WHERE name LIKE %s OR location LIKE %s",
            ['%' + query + '%', '%' + query + '%']
        )
        hotels = cursor.fetchall()
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM hotels")
        hotels = cursor.fetchall()
    return render(request, 'search-page.html', {'hotels': hotels, 'query': query})