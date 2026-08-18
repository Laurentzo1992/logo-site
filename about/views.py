import json
import os
import re
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from about.models import About_Us
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from utils.htmx import htmx_toast, is_htmx
from utils.ratelimit import rate_limit_json
import logging

logger = logging.getLogger(__name__)

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
    except OSError:
        logger.exception("Erreur inattendue lors du chargement de labels.json")
        return HttpResponse("Une erreur est survenue. Veuillez réessayer plus tard.", status=500)

    abouts = About_Us.objects.all()

    if not abouts:
        labels["warning"] = "Aucune information disponible"

    return render(request, "about/about.html", {"abouts": abouts, "labels": labels})









def _contact_response(request, message, success, status=200):
    """htmx -> toast (rien à re-rendre) ; sinon -> message Django + retour à la page."""
    if is_htmx(request):
        return htmx_toast(message, success=success, status=status)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@rate_limit_json("contact_mail", limit=5, period=60)
def contact_mail(request):
    """
    Vue pour traiter les demandes de contact et envoyer un email.
    Nécessite les champs: nom, email, message
    Champs optionnels: telephone, service
    """
    try:
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        message_txt = request.POST.get('message')
        telephone = request.POST.get('telephone', '')
        service = request.POST.get('service', '')

        # Vérifier que les champs obligatoires sont présents
        if not all([nom, email, message_txt]):
            return _contact_response(
                request, "Certains champs obligatoires sont manquants (nom, email, message)",
                success=False, status=400,
            )

        # Valider le format de l'email avec une expression régulière simple
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return _contact_response(request, "Format d'email invalide", success=False, status=400)

        # Construire le message complet
        full_message = f"""
        Nom du client: {nom}
        Email du client: {email}
        Téléphone du client: {telephone}
        Service demandé par le client: {service}

        Message:
        {message_txt}
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
        return _contact_response(request, "Message envoyé avec succès.", success=True)

    except Exception:
        logger.exception("Erreur lors de l'envoi de l'email de contact")
        return _contact_response(
            request, "Une erreur est survenue lors de l'envoi du message. Veuillez réessayer plus tard.",
            success=False, status=500,
        )















