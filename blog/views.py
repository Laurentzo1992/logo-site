from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from utils.cons import ARTICLES_PER_PAGE
from .models import Article, Category, Tag, Comment, NewsletterSubscriber


def blog(request):
    return render(request, 'blog/blog.html')



def _sidebar_context():
    """Contexte commun à toutes les vues (sidebar)."""
    return {
        "categories":      Category.objects.annotate(
                               count=Count("articles", filter=Q(articles__status=Article.Status.PUBLISHED))
                           ).order_by("order", "name"),
        "popular_articles": Article.objects.filter(status=Article.Status.PUBLISHED)
                                .order_by("-views")[:4],
        "recent_articles":  Article.objects.filter(status=Article.Status.PUBLISHED)
                                .order_by("-published_at")[:4],
        "popular_tags":     Tag.objects.annotate(
                                count=Count("articles", filter=Q(articles__status=Article.Status.PUBLISHED))
                            ).order_by("-count")[:12],
        "total_articles":   Article.objects.filter(status=Article.Status.PUBLISHED).count(),
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
    return render(request, "blog/index.html", ctx)


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
    return redirect(f"/blog/?category={slug}")


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
    return render(request, "blog/index.html", ctx)


# ─── Actions POST ──────────────────────────────────────────────────────────────

@require_POST
def add_comment(request, slug):
    """Soumission d'un commentaire (visiteur ou utilisateur connecté)."""
    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)

    content = request.POST.get("content", "").strip()
    if not content:
        messages.error(request, "Le commentaire ne peut pas être vide.")
        return redirect(article.get_absolute_url())

    comment = Comment(article=article, content=content)

    if request.user.is_authenticated:
        comment.author = request.user
    else:
        name  = request.POST.get("guest_name", "").strip()
        email = request.POST.get("guest_email", "").strip()
        if not name:
            messages.error(request, "Veuillez indiquer votre nom.")
            return redirect(article.get_absolute_url())
        comment.guest_name  = name
        comment.guest_email = email

    comment.save()
    messages.success(request, "Votre commentaire est en attente de modération.")
    return redirect(article.get_absolute_url())


@require_POST
def newsletter_subscribe(request):
    """Inscription à la newsletter (JSON ou form classique)."""
    email = request.POST.get("email", "").strip()

    if not email:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Email requis."}, status=400)
        messages.error(request, "Email requis.")
        return redirect(request.META.get("HTTP_REFERER", "/blog/"))

    _, created = NewsletterSubscriber.objects.get_or_create(email=email)

    msg = "Merci ! Vous êtes bien inscrit." if created else "Vous êtes déjà abonné."

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "message": msg})

    messages.success(request, msg)
    return redirect(request.META.get("HTTP_REFERER", "/blog/"))


def search_view(request):
    """Recherche globale — redirige vers index avec param q."""
    q = request.GET.get("q", "")
    return redirect(f"/blog/?q={q}")