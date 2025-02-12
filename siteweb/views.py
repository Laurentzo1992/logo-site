import json
import os
from django.shortcuts import render
from django.conf import settings

# Récupération du chemin du dossier contenant les fichiers JSON
LIBELLE_DIR = settings.LIBELLE_FILE_DIR 

def index(request):
    labels_file = os.path.join(LIBELLE_DIR, "labels.json")

    try:
        with open(labels_file, "r", encoding="utf-8") as file:
            labels = json.load(file)
    except FileNotFoundError:
        labels = {}
    except json.JSONDecodeError:
        labels = {"error": "Fichier JSON invalide"} 
    #print(labels)
    return render(request, "base.html", {"labels": labels})



