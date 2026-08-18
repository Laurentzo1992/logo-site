# -*- coding: utf-8 -*-
"""Configuration des flux RSS utilisés par `manage.py fetch_news` pour
alimenter automatiquement le blog (veille : extrait + lien vers la source,
jamais l'article complet — voir blog/management/commands/fetch_news.py).

Pour ajouter une source : ajoute une entrée à FEEDS. "limit" borne le nombre
d'entrées importées par flux à chaque exécution (le flux entier est relu à
chaque fois, mais les articles déjà importés — même source_url — sont
ignorés automatiquement). "require_keywords" (optionnel) est un filtre de
pertinence : l'article est ignoré si aucun de ces mots-clés n'apparaît dans
son titre/résumé — utile pour les flux généralistes qui mélangent des sujets
hors périmètre (jeux vidéo, cinéma, actualité people...).
"""

# Filtre de pertinence pour les flux généralistes — on ne veut que du contenu
# qui a un lien avec l'activité de LOGO SERVICES (ingénierie logicielle,
# infrastructure, IA, numérisation, formation).
TECH_RELEVANCE_KEYWORDS = [
    "logiciel", "application", "app ", "cloud", "données", "data",
    "cybersécurité", "cyberattaque", "sécurité informatique", "sécurité",
    "intelligence artificielle", " ia ", " ia,", " ia.", "ia,",
    "numérique", "digital", "transformation digitale", "entreprise",
    "informatique", "système d'information", "réseau", "serveur",
    "startup", "innovation technologique", "développeur", "développement",
    "infrastructure", "base de données", "archivage", "numérisation",
    "formation", "e-learning",
]

FEEDS = [
    # --- Cybersécurité ---
    {
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "source_name": "The Hacker News",
        "category": "Cybersécurité",
        "category_icon": "🔐",
        "icon": "🔐",
        "tags": ["Cybersécurité"],
        "limit": 6,
    },
    {
        "url": "https://www.bleepingcomputer.com/feed/",
        "source_name": "BleepingComputer",
        "category": "Cybersécurité",
        "category_icon": "🔐",
        "icon": "🔐",
        "tags": ["Cybersécurité"],
        "limit": 6,
    },
    {
        "url": "https://www.zataz.com/feed/",
        "source_name": "ZATAZ",
        "category": "Cybersécurité",
        "category_icon": "🔐",
        "icon": "🔐",
        "tags": ["Cybersécurité"],
        "limit": 6,
    },

    # --- Intelligence Artificielle ---
    {
        "url": "https://www.lemondeinformatique.fr/flux-rss/thematique/intelligence-artificielle/rss.xml",
        "source_name": "Le Monde Informatique",
        "category": "Intelligence Artificielle",
        "category_icon": "🤖",
        "icon": "🤖",
        "tags": ["Intelligence Artificielle"],
        "limit": 6,
    },
    {
        "url": "http://export.arxiv.org/rss/cs.AI",
        "source_name": "arXiv (cs.AI)",
        "category": "Intelligence Artificielle",
        "category_icon": "🤖",
        "icon": "🧠",
        "tags": ["Intelligence Artificielle", "Recherche"],
        "limit": 8,
    },
    {
        "url": "http://export.arxiv.org/rss/cs.CL",
        "source_name": "arXiv (cs.CL)",
        "category": "Intelligence Artificielle",
        "category_icon": "🤖",
        "icon": "🧠",
        "tags": ["LLM", "NLP", "Recherche"],
        "limit": 8,
    },

    # --- Tech générale / transformation digitale ---
    # Seule source généraliste restante (Numerama retiré : trop de contenu
    # hors sujet — jeux vidéo, cinéma...). Filtrée par mots-clés pour rester
    # strictement dans le périmètre de l'activité de LOGO SERVICES.
    {
        "url": "https://www.lemondeinformatique.fr/flux-rss/thematique/actualites/rss.xml",
        "source_name": "Le Monde Informatique",
        "category": "Tech & Transformation Digitale",
        "category_icon": "💻",
        "icon": "💻",
        "tags": ["Transformation Digitale"],
        "limit": 6,
        "require_keywords": TECH_RELEVANCE_KEYWORDS,
    },
]

# Tags additionnels attribués automatiquement quand le titre/résumé d'un
# article matche un de ces mots-clés — couvre les thématiques niches
# (archivage/GED, langues africaines) qui n'ont pas de flux RSS dédié.
KEYWORD_TAGS = {
    "Archivage & IA": [
        "archivage", "archival", "records management", "gestion électronique de document",
        "ged ", "gestion documentaire", "document management", "ocr", "dématérialisation",
    ],
    "Langues Africaines": [
        "african language", "langue africaine", "langues africaines", "swahili", "kiswahili",
        "yoruba", "hausa", "wolof", "bambara", "fulani", "fula", "amharic", "afrikaans",
        "low-resource african", "africa nlp", "nlp africa",
    ],
}
