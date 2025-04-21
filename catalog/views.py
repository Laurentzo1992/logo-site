from django.shortcuts import render
from catalog.models import Projet
from django.http import HttpResponse, JsonResponse

def catalog(request):
    categorie_id = request.GET.get('categorie')
    
    if categorie_id:
        projets = Projet.objects.filter(categorie_id=categorie_id)
    else:
        projets = Projet.objects.all()
        
    context = {'projets': projets}
    return render(request, 'catalog/catalog.html', context)


