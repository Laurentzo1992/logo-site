from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug        = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    icon        = models.CharField(max_length=10, blank=True, verbose_name="Emoji icône")
    order       = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="Tag")
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):

    class Status(models.TextChoices):
        DRAFT     = "draft",     "Brouillon"
        PUBLISHED = "published", "Publié"
        ARCHIVED  = "archived",  "Archivé"

    # Contenu
    title       = models.CharField(max_length=250, verbose_name="Titre")
    slug        = models.SlugField(max_length=280, unique=True, blank=True)
    excerpt     = models.TextField(max_length=400, verbose_name="Résumé court")
    content     = models.TextField(verbose_name="Contenu (HTML/Markdown)")
    thumbnail   = models.ImageField(
        upload_to="blog/thumbnails/%Y/%m/",
        blank=True, null=True,
        verbose_name="Image de couverture"
    )
    icon        = models.CharField(
        max_length=10, blank=True,
        verbose_name="Emoji icône (fallback si pas d'image)"
    )

    # Taxonomie
    category    = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="articles",
        verbose_name="Catégorie"
    )
    tags        = models.ManyToManyField(
        Tag, blank=True,
        related_name="articles",
        verbose_name="Tags"
    )

    # Auteur
    author      = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="articles",
        verbose_name="Auteur"
    )

    # Statut et dates
    status      = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Statut"
    )
    is_featured = models.BooleanField(default=False, verbose_name="Article à la une")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de publication")

    # Métriques
    views       = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    read_time   = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Temps de lecture (min)"
    )

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Calcul automatique du temps de lecture (~200 mots/min)
        word_count = len(self.content.split())
        self.read_time = max(1, round(word_count / 200))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    def increment_views(self):
        Article.objects.filter(pk=self.pk).update(views=models.F("views") + 1)


class Comment(models.Model):
    article    = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Article"
    )
    author     = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="comments",
        verbose_name="Auteur"
    )
    guest_name  = models.CharField(max_length=100, blank=True, verbose_name="Nom (visiteur)")
    guest_email = models.EmailField(blank=True, verbose_name="Email (visiteur)")
    content    = models.TextField(verbose_name="Commentaire")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    def __str__(self):
        name = self.author.get_full_name() if self.author else self.guest_name
        return f"{name} → {self.article.title[:40]}"


class NewsletterSubscriber(models.Model):
    email       = models.EmailField(unique=True, verbose_name="Email")
    is_active   = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"

    def __str__(self):
        return self.email
