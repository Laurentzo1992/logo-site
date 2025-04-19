import json
import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from about.models import About_Us, Contact
from bs4 import BeautifulSoup
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods
import logging

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




def api_about(request):
    abouts = About_Us.objects.all()
    data = []

    for about in abouts:
        soup = BeautifulSoup(about.contenu or "", "html.parser")
        text = soup.get_text().strip()

        data.append({
            "fichier": about.fichier.url if about.fichier else "",
            "contenu": text,
        })

    return JsonResponse(data, safe=False)




def api_contact(request):
    contacts = Contact.objects.all()
    data = []

    for contact in contacts:
        # Nettoyage HTML séparé
        adresse_text = BeautifulSoup(contact.adresse or "", "html.parser").get_text().strip()
        heure_text = BeautifulSoup(contact.heure_ouverture or "", "html.parser").get_text().strip()

        data.append({
            "telephone": contact.telephone,
            "heure_ouverture": heure_text,
            "adresse": adresse_text,
            "email": contact.email
        })

    return JsonResponse(data, safe=False)






# Configurer le logger
logger = logging.getLogger(__name__)

@csrf_exempt
def contact_mail(request):
    """
    Vue pour traiter les demandes de contact et envoyer un email.
    Nécessite les champs: nom, email, message
    Champs optionnels: telephone, service
    """
    try:
        # Valider et parser les données JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Format JSON invalide"}, status=400)
        
        # Extraire et valider les champs requis
        nom = data.get('nom')
        email = data.get('email')
        message = data.get('message')
        telephone = data.get('telephone')
        service = data.get('service')
        
        # Vérifier que les champs obligatoires sont présents
        if not all([nom, email, message, telephone, service]):
            return JsonResponse({
                "success": False, 
                "message": "Certains champs obligatoires sont manquants (nom, email, message)"
            }, status=400)
        
        # Valider le format de l'email avec une expression régulière simple
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({
                "success": False, 
                "message": "Format d'email invalide"
            }, status=400)
        
        # Extraire les champs optionnels
        telephone = data.get('telephone', '')
        service = data.get('service', '')
        
        # Construire le message complet
        full_message = f"""
        Nom du client: {nom}
        Email du client: {email}
        Téléphone du client: {telephone}
        Service demandé par le client: {service}
        
        Message:
        {message}
        """
        
        # Envoyer l'email
        send_mail(
            subject=f"Message de contact de {nom}",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['lnikiema9@gmail.com', 'laurent.nikiema@logo-services.com', 'bzakaria.topan@logo-services.com'],
            fail_silently=False,
        )
        
        logger.info(f"Email de contact envoyé avec succès pour {email}")
        return JsonResponse({"success": True, "message": "Message envoyé avec succès."})
    
    except Exception as e:
        # Journaliser l'erreur pour le débogage
        logger.error(f"Erreur lors de l'envoi de l'email de contact: {str(e)}")
        return JsonResponse({
            "success": False, 
            "message": "Une erreur est survenue lors de l'envoi du message. Veuillez réessayer plus tard."
        }, status=500)















