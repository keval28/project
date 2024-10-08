from django.shortcuts import render
from .models import DataModel

def search(request):
    query = request.GET.get('keyword')
    if query:
        results = DataModel.objects.filter(name__icontains=query)  # or any other field
    else:
        results = []
    return render(request, 'searchapp/search.html', {'results': results, 'query': query})