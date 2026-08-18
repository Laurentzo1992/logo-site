import json
import logging
import os
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from about.models import About_Us, Contact
from siteweb.models import Services, Newletter_Email
from bs4 import BeautifulSoup
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from utils.htmx import htmx_toast, is_htmx
from utils.ratelimit import rate_limit_json

logger = logging.getLogger(__name__)

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

    contact = Contact.objects.first()
    contact_display = None
    if contact:
        contact_display = {
            "adresse": BeautifulSoup(contact.adresse or "", "html.parser").get_text().strip(),
            "telephone": contact.telephone,
            "email": contact.email,
            "heure_ouverture": BeautifulSoup(contact.heure_ouverture or "", "html.parser").get_text().strip(),
        }

    return render(request, "siteweb/index.html", {
        "labels": labels,
        "services": Services.objects.all(),
        "abouts": About_Us.objects.all(),
        "contact": contact_display,
    })



def _newsletter_response(request, message, success, status=200):
    if is_htmx(request):
        return htmx_toast(message, success=success, status=status)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@rate_limit_json("subscribe_newsletter", limit=5, period=60)
def subscribe_newsletter(request):
    email = request.POST.get('email', '').strip()

    if not email:
        return _newsletter_response(request, "L'email est requis.", success=False, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return _newsletter_response(request, "Format d'email invalide.", success=False, status=400)

    if Newletter_Email.objects.filter(email=email).exists():
        return _newsletter_response(request, "Cet email est déjà abonné.", success=False, status=400)

    try:
        Newletter_Email.objects.create(email=email)
    except Exception:
        logger.exception("Erreur lors de l'inscription à la newsletter pour %s", email)
        return _newsletter_response(
            request, "Une erreur est survenue. Veuillez réessayer plus tard.", success=False, status=500,
        )

    return _newsletter_response(request, "Merci pour votre abonnement !", success=True)
