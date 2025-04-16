import json
import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from about.models import About_Us
# Récupération du chemin du dossier contenant les fichiers JSON
LIBELLE_DIR = settings.LIBELLE_FILE_DIR 


def about(request):
    labels_file = os.path.join(LIBELLE_DIR, "labels.json")

    try:
        with open(labels_file, "r", encoding="utf-8") as file:
            labels = json.load(file)
    except FileNotFoundError:
        labels = {}
    except json.JSONDecodeError:
        labels = {"error": "Fichier JSON invalide"}
    except Exception as e:
        return HttpResponse(f"Erreur inattendue : {e}", status=500)

    abouts = About_Us.objects.all()

    if not abouts:
        labels["warning"] = "Aucune information disponible"

    return render(request, "about/aboute.html", {"abouts": abouts, "labels": labels})