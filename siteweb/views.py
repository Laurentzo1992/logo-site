import json
import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from siteweb.models import Services, Newletter_Email
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
    return render(request, "siteweb/index.html", {"labels": labels})



def api_services(request):
    services = Services.objects.all()
    data = []

    for service in services:
        # Nettoyer le HTML
        soup = BeautifulSoup(service.description, "html.parser")
        text = soup.get_text().strip()

        data.append({
            "libelle": service.libelle,
            "description": text,
            "icon": service.icon,
        })

    return JsonResponse(data, safe=False)







@csrf_exempt
def subscribe_newsletter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({"success": False, "message": "L'email est requis."}, status=400)

            # Validation de l'email
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({"success": False, "message": "Format d'email invalide."}, status=400)

            if Newletter_Email.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Cet email est déjà abonné."}, status=400)

            Newletter_Email.objects.create(email=email)
            return JsonResponse({"success": True, "message": "Merci pour votre abonnement !"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
