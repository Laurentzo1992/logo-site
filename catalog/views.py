from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from catalog.models import Categorie_Projet, Projet
from utils.htmx import is_htmx


def catalog(request):
    categorie_id = request.GET.get('categorie')

    if categorie_id and categorie_id.isdigit():
        projets = Projet.objects.filter(categorie_id=categorie_id)
    else:
        projets = Projet.objects.all()

    categories = Categorie_Projet.objects.annotate(count=Count('projet')).order_by('libelle')

    context = {
        'projets': projets,
        'categories': categories,
        'active_categorie_id': categorie_id if categorie_id and categorie_id.isdigit() else None,
    }

    if is_htmx(request):
        html = render_to_string('catalog/partials/filter_oob.html', context, request=request)
        html += render_to_string('catalog/partials/grid.html', context, request=request)
        return HttpResponse(html)

    return render(request, 'catalog/catalog.html', context)
