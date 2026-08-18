# -*- coding: utf-8 -*-
"""Récupère des articles depuis des flux RSS externes (voir blog/rss_sources.py)
et les publie sur le blog sous forme de veille : titre + court extrait +
lien explicite vers la source. On ne republie jamais le texte intégral d'un
tiers (risque de droit d'auteur) — voir la discussion avec le client avant
l'implémentation de cette commande.

Idempotent : chaque entrée de flux est identifiée par son URL (source_url),
donc relancer la commande n'importe pas deux fois le même article.
"""
from datetime import datetime, timezone as dt_timezone

import feedparser
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Article, Category, Tag
from blog.rss_sources import FEEDS, KEYWORD_TAGS


def clean_html(raw):
    if not raw:
        return ""
    return BeautifulSoup(raw, "html.parser").get_text(separator=" ").strip()


def build_excerpt(summary, title, limit=380):
    text = summary or title
    if len(text) <= limit:
        return text
    truncated = text[:limit].rsplit(" ", 1)[0]
    return f"{truncated}…"


class Command(BaseCommand):
    help = "Récupère des articles de veille (extrait + lien source) depuis des flux RSS et les publie sur le blog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Affiche ce qui serait importé sans rien écrire en base.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        total_created = 0
        total_skipped = 0
        total_filtered = 0

        for feed_cfg in FEEDS:
            source_name = feed_cfg["source_name"]
            parsed = feedparser.parse(feed_cfg["url"])

            if parsed.bozo and not parsed.entries:
                self.stderr.write(self.style.WARNING(
                    f"Flux illisible, ignoré : {feed_cfg['url']} ({parsed.get('bozo_exception')})"
                ))
                continue

            category = None
            if not dry_run:
                category, _ = Category.objects.get_or_create(
                    name=feed_cfg["category"],
                    defaults={"icon": feed_cfg.get("category_icon", "📰")},
                )

            for entry in parsed.entries[: feed_cfg.get("limit", 6)]:
                link = entry.get("link")
                if not link:
                    continue

                if Article.objects.filter(source_url=link).exists():
                    total_skipped += 1
                    continue

                title = clean_html(entry.get("title", "")).strip()
                if not title:
                    continue

                summary = clean_html(entry.get("summary") or entry.get("description") or "")
                haystack = f"{title} {summary}".lower()

                require_keywords = feed_cfg.get("require_keywords")
                if require_keywords and not any(kw in haystack for kw in require_keywords):
                    total_filtered += 1
                    continue

                excerpt = build_excerpt(summary, title)
                content = f"{summary or title}\n\n**Source :** [{source_name}]({link})"

                keyword_tags = [
                    tag_name
                    for tag_name, keywords in KEYWORD_TAGS.items()
                    if any(kw in haystack for kw in keywords)
                ]

                published_at = timezone.now()
                if entry.get("published_parsed"):
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=dt_timezone.utc)

                if dry_run:
                    self.stdout.write(f"[dry-run] + {title} ({source_name})")
                    total_created += 1
                    continue

                article = Article.objects.create(
                    title=title[:250],
                    excerpt=excerpt[:400],
                    content=content,
                    category=category,
                    status=Article.Status.PUBLISHED,
                    published_at=published_at,
                    icon=feed_cfg.get("icon", "📰"),
                    source_name=source_name,
                    source_url=link,
                )

                for tag_name in feed_cfg.get("tags", []) + keyword_tags:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    article.tags.add(tag)

                total_created += 1
                self.stdout.write(f"+ {article.title} ({source_name})")

        self.stdout.write(self.style.SUCCESS(
            f"Terminé : {total_created} article(s) importé(s), {total_skipped} déjà présent(s), "
            f"{total_filtered} hors-sujet ignoré(s)."
        ))
