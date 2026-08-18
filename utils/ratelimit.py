import functools

from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect

from utils.htmx import htmx_toast, is_htmx


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


RATE_LIMIT_MESSAGE = "Trop de requêtes. Veuillez réessayer dans quelques instants."


def rate_limit_json(key_prefix, limit=5, period=60):
    """Limite le nombre d'appels par IP sur une fenêtre glissante simple.

    Réponse adaptée au type de requête : toast htmx, JSON classique, ou
    redirection avec message Django (repli sans JS).

    Best-effort (cache en mémoire du process) : pense a passer sur un cache
    partage (Redis/Memcached) si l'app tourne avec plusieurs workers/replicas.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped(request, *args, **kwargs):
            cache_key = f"ratelimit:{key_prefix}:{_client_ip(request)}"
            count = cache.get(cache_key, 0)
            if count >= limit:
                if is_htmx(request):
                    return htmx_toast(RATE_LIMIT_MESSAGE, success=False, status=429)
                if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                    return JsonResponse({"success": False, "message": RATE_LIMIT_MESSAGE}, status=429)
                messages.error(request, RATE_LIMIT_MESSAGE)
                return redirect(request.META.get("HTTP_REFERER", "/"))
            cache.set(cache_key, count + 1, period)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
