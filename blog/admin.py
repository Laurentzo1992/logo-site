# blog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import Article, Category, Tag, Comment, NewsletterSubscriber


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("icon", "name", "slug", "article_count", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Articles")
    def article_count(self, obj):
        return obj.articles.filter(status=Article.Status.PUBLISHED).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "article_count")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Articles")
    def article_count(self, obj):
        return obj.articles.count()


class CommentInline(admin.TabularInline):
    model  = Comment
    extra  = 0
    fields = ("author", "guest_name", "content", "is_approved", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display   = ("title", "category", "source_name", "author", "status", "is_featured", "views", "read_time", "published_at")
    list_filter    = ("status", "is_featured", "category", "source_name")
    search_fields  = ("title", "excerpt", "content", "source_name")
    list_editable  = ("status", "is_featured")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal   = ("tags",)
    readonly_fields     = ("views", "read_time", "created_at", "updated_at")
    inlines             = [CommentInline]
    actions             = ["publish", "archive"]
    date_hierarchy      = "published_at"

    fieldsets = (
        ("Contenu", {
            "fields": ("title", "slug", "excerpt", "content", "icon", "thumbnail")
        }),
        ("Taxonomie", {
            "fields": ("category", "tags")
        }),
        ("Publication", {
            "fields": ("author", "status", "is_featured", "published_at")
        }),
        ("Veille externe", {
            "fields": ("source_name", "source_url"),
            "description": "Renseigné automatiquement par `manage.py fetch_news` pour les articles de veille.",
            "classes": ("collapse",)
        }),
        ("Métriques (auto)", {
            "fields": ("views", "read_time", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    @admin.action(description="Publier les articles sélectionnés")
    def publish(self, request, queryset):
        queryset.update(status=Article.Status.PUBLISHED, published_at=now())

    @admin.action(description="Archiver les articles sélectionnés")
    def archive(self, request, queryset):
        queryset.update(status=Article.Status.ARCHIVED)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ("__str__", "is_approved", "created_at")
    list_filter   = ("is_approved",)
    list_editable = ("is_approved",)
    actions       = ["approve"]

    @admin.action(description="Approuver les commentaires sélectionnés")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter  = ("is_active",)
    list_editable = ("is_active",)
