import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify")
def markdownify(text):
    """Rend le champ Article.content (Markdown ou HTML rédigé par un membre
    de l'équipe via l'admin) en HTML. Contenu de confiance (staff uniquement),
    comme les autres champs TinyMCE du site."""
    if not text:
        return ""
    return mark_safe(md.markdown(text, extensions=["extra", "sane_lists"]))
