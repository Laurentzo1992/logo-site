import json

from django.http import HttpResponse


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def htmx_toast(message, success=True, status=200, swap_none=True):
    """Réponse vide (par défaut) qui déclenche le toast global côté client
    via l'en-tête HX-Trigger, sans rien re-rendre dans le DOM. Voir le
    listener 'toast' dans templates/base.html."""
    response = HttpResponse(status=status)
    response["HX-Trigger"] = json.dumps({
        "toast": {"message": message, "type": "success" if success else "danger"},
    })
    if swap_none:
        response["HX-Reswap"] = "none"
    return response
