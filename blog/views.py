from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from utils.cons import ARTICLES_PER_PAGE
from utils.htmx import htmx_toast, is_htmx
from utils.ratelimit import rate_limit_json
from .models import Article, Category, Tag, Comment, NewsletterSubscriber


def _blog_response(request, ctx):
    """Page complète normalement ; en htmx, ne renvoie que la barre de
    catégories (en out-of-band swap) + la grille/pagination ciblées par
    #blog-main-inner — voir blog/partials/."""
    if is_htmx(request):
        html = render_to_string("blog/partials/cats_oob.html", ctx, request=request)
        html += render_to_string("blog/partials/results.html", ctx, request=request)
        return HttpResponse(html)
    return render(request, "blog/index.html", ctx)


def _sidebar_context():
    """Contexte commun à toutes les vues (sidebar + stats du hero)."""
    published = Article.objects.filter(status=Article.Status.PUBLISHED)
    return {
        "categories":      Category.objects.annotate(
                               count=Count("articles", filter=Q(articles__status=Article.Status.PUBLISHED))
                           ).order_by("order", "name"),
        "popular_articles": published.order_by("-views")[:4],
        "recent_articles":  published.order_by("-published_at")[:4],
        "popular_tags":     Tag.objects.annotate(
                                count=Count("articles", filter=Q(articles__status=Article.Status.PUBLISHED))
                            ).order_by("-count")[:12],
        "total_articles":   published.count(),
        "total_views":      published.aggregate(total=Sum("views"))["total"] or 0,
        "total_authors":    published.exclude(author__isnull=True).values("author").distinct().count(),
    }


def _published():
    return Article.objects.filter(status=Article.Status.PUBLISHED).select_related(
        "author", "category"
    ).prefetch_related("tags")


# ─── Vues principales ──────────────────────────────────────────────────────────

def blog_index(request):
    """Page principale du blog : liste + filtres."""
    qs = _published()

    # Filtre catégorie (GET param)
    category_slug = request.GET.get("category")
    active_category = None
    if category_slug and category_slug != "all":
        active_category = get_object_or_404(Category, slug=category_slug)
        qs = qs.filter(category=active_category)

    # Recherche texte (GET param)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(excerpt__icontains=q)
            | Q(content__icontains=q)
            | Q(tags__name__icontains=q)
        ).distinct()

    # Article à la une (indépendant du filtre)
    featured = (
        Article.objects.filter(status=Article.Status.PUBLISHED, is_featured=True)
        .select_related("author", "category")
        .first()
    )

    # Pagination
    paginator   = Paginator(qs, ARTICLES_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj    = paginator.get_page(page_number)

    ctx = {
        "page_obj":        page_obj,
        "featured":        featured,
        "active_category": active_category,
        "search_query":    q,
        **_sidebar_context(),
    }
    return _blog_response(request, ctx)


def article_detail(request, slug):
    """Détail d'un article + compteur de vues + commentaires."""
    article = get_object_or_404(
        Article.objects.select_related("author", "category").prefetch_related("tags", "comments__author"),
        slug=slug,
        status=Article.Status.PUBLISHED,
    )

    # Incrément vues (atomic, évite les race conditions)
    article.increment_views()

    # Articles liés (même catégorie, sauf lui-même)
    related = (
        _published()
        .filter(category=article.category)
        .exclude(pk=article.pk)[:3]
        if article.category
        else Article.objects.none()
    )

    # Commentaires approuvés
    comments = article.comments.filter(is_approved=True).select_related("author")

    ctx = {
        "article":  article,
        "related":  related,
        "comments": comments,
        **_sidebar_context(),
    }
    return render(request, "blog/detail.html", ctx)


def category_view(request, slug):
    """Filtre par catégorie — redirige vers index avec param GET."""
    return redirect(f"{reverse('blog')}?{urlencode({'category': slug})}")


def tag_view(request, slug):
    """Articles filtrés par tag."""
    tag = get_object_or_404(Tag, slug=slug)
    qs  = _published().filter(tags=tag)

    paginator   = Paginator(qs, ARTICLES_PER_PAGE)
    page_obj    = paginator.get_page(request.GET.get("page", 1))

    ctx = {
        "page_obj":   page_obj,
        "active_tag": tag,
        **_sidebar_context(),
    }
    return _blog_response(request, ctx)


# ─── Actions POST ──────────────────────────────────────────────────────────────

@require_POST
@rate_limit_json("add_comment", limit=10, period=60)
def add_comment(request, slug):
    """Soumission d'un commentaire (visiteur ou utilisateur connecté)."""
    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)

    def respond(level, message):
        getattr(messages, level)(request, message)
        if is_htmx(request):
            comments = article.comments.filter(is_approved=True).select_related("author")
            return render(request, "blog/partials/comments.html", {"article": article, "comments": comments})
        return redirect(f"{article.get_absolute_url()}#comments")

    content = request.POST.get("content", "").strip()
    if not content:
        return respond("error", "Le commentaire ne peut pas être vide.")

    comment = Comment(article=article, content=content)

    if request.user.is_authenticated:
        comment.author = request.user
    else:
        name  = request.POST.get("guest_name", "").strip()
        email = request.POST.get("guest_email", "").strip()
        if not name:
            return respond("error", "Veuillez indiquer votre nom.")
        comment.guest_name  = name
        comment.guest_email = email

    comment.save()
    return respond("success", "Merci ! Votre commentaire a été publié.")


@require_POST
@rate_limit_json("newsletter_subscribe", limit=5, period=60)
def newsletter_subscribe(request):
    """Inscription à la newsletter (htmx ou form classique)."""
    email = request.POST.get("email", "").strip()

    if not email:
        if is_htmx(request):
            return htmx_toast("Email requis.", success=False, status=400)
        messages.error(request, "Email requis.")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog")))

    _, created = NewsletterSubscriber.objects.get_or_create(email=email)

    msg = "Merci ! Vous êtes bien inscrit." if created else "Vous êtes déjà abonné."

    if is_htmx(request):
        return htmx_toast(msg, success=True)

    messages.success(request, msg)
    return redirect(request.META.get("HTTP_REFERER", reverse("blog")))


def search_view(request):
    """Recherche globale — redirige vers index avec param q."""
    q = request.GET.get("q", "")
    return redirect(f"{reverse('blog')}?{urlencode({'q': q})}")
