# -*- coding: utf-8 -*-
"""Nettoie les 2 projets existants et ajoute les 10 references de projets
similaires fournies par le client (document de reference LOGO SERVICES)."""
import django
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logosite.settings")
django.setup()

from catalog.models import Categorie_Projet, Projet


def strip_html(value):
    if not value:
        return value
    text = re.sub(r"<[^>]+>", "", value)
    text = (
        text.replace("&eacute;", "é")
        .replace("&egrave;", "è")
        .replace("&agrave;", "à")
        .replace("&rsquo;", "'")
        .replace("&ecirc;", "ê")
        .replace("&ocirc;", "ô")
        .replace("&nbsp;", " ")
    )
    return text.strip()


# --- 1. Nettoyage des 2 projets existants (HTML residuel dans des champs texte brut) ---
for p in Projet.objects.all():
    changed = False
    for field in ("defis", "solution", "resultat"):
        old = getattr(p, field)
        new = strip_html(old)
        if new != old:
            setattr(p, field, new)
            changed = True
    if changed:
        p.save()
        print(f"Nettoye: {p.nom_client}")

# --- 2. Categories (deja existantes en base) ---
genie_logiciel, _ = Categorie_Projet.objects.get_or_create(libelle="Génie Logiciel")
numerisation, _ = Categorie_Projet.objects.get_or_create(libelle="Numérisation de Documents")

REFERENCES = [
    dict(
        nom_client="SONABHY",
        intitule="Ajout des modules OCR et LAD/RAD dans DocuBase au profit de la SONABHY",
        annee_execution="2025 - 2026",
        categorie=numerisation,
        defis="Automatiser la reconnaissance et l'extraction d'informations dans les documents numérisés pour réduire la saisie manuelle.",
        solution="Intégration des modules OCR et LAD/RAD dans DocuBase, configuration des règles d'indexation documentaire et automatisation du classement des documents.",
        resultat="Réduction des opérations de saisie manuelle et amélioration de la recherche d'informations dans les documents numérisés.",
    ),
    dict(
        nom_client="INSD",
        intitule="Acquisition d'un logiciel de gestion du plan de passation des marchés de l'INSD",
        annee_execution="2025",
        categorie=genie_logiciel,
        defis="Centraliser et sécuriser le suivi des procédures et échéances de passation des marchés.",
        solution="Déploiement d'un logiciel dédié à la gestion et à la planification du plan de passation des marchés, avec production de tableaux de bord de suivi.",
        resultat="Centralisation sécurisée des informations et automatisation du suivi des échéances de passation des marchés.",
    ),
    dict(
        nom_client="Agence de l'Eau du Nakambé",
        intitule="Conception d'une base de données informatisée pour le suivi-évaluation et la capitalisation du SDAGE et du PPI",
        annee_execution="2025",
        categorie=genie_logiciel,
        defis="Centraliser le suivi-évaluation et la capitalisation des données du SDAGE et du PPI de l'espace de compétences de l'Agence.",
        solution="Conception et mise en place d'une base de données informatisée avec tableaux de bord de suivi des indicateurs et des projets.",
        resultat="Sécurisation, mise à jour et facilitation de l'exploitation des données de suivi-évaluation.",
    ),
    dict(
        nom_client="Ministère de l'Economie, des Finances et de la Prospective (DGSI)",
        intitule="Acquisition et déploiement d'une plateforme de gestion des formations Moodle au profit de la DGSI",
        annee_execution="2024",
        categorie=genie_logiciel,
        defis="Doter la DGSI d'une plateforme centralisée de gestion des formations, des apprenants et des contenus pédagogiques.",
        solution="Installation, configuration et déploiement de la plateforme Moodle avec gestion des cours, des inscriptions et des évaluations.",
        resultat="Suivi centralisé de la participation et des résultats aux formations, avec production de statistiques.",
    ),
    dict(
        nom_client="Ministère de l'Agriculture des Ressources Animales et Halieutiques",
        intitule="Mise en place d'un système d'archivage physique et électronique et d'un manuel de référentiel de gestion des archives (PRSA-BF)",
        annee_execution="2024",
        categorie=numerisation,
        defis="Structurer et sécuriser la gestion des fonds d'archives physiques et électroniques dans le cadre du PRSA-BF.",
        solution="Analyse des fonds existants, élaboration d'un plan de classement et d'un manuel de référentiel de gestion des archives.",
        resultat="Mise en place de règles de conservation et d'un dispositif de sécurisation et de sauvegarde des archives électroniques.",
    ),
    dict(
        nom_client="ANEEMAS",
        intitule="Maintenance des applications et extension de la base de données SIG de l'ANEEMAS",
        annee_execution="2024",
        categorie=genie_logiciel,
        defis="Maintenir et faire évoluer les applications et la base de données SIG existantes de l'ANEEMAS.",
        solution="Maintenance corrective et évolutive des applications, mise à jour de la base de données SIG et intégration de nouveaux modules fonctionnels.",
        resultat="Amélioration des performances applicatives et mise en place d'outils de consultation et d'analyse des données SIG.",
    ),
    dict(
        nom_client="Fonds de Développement Culturel et Touristique (FDCT)",
        intitule="Archivage électronique des dossiers du FDCT",
        annee_execution="2024",
        categorie=numerisation,
        defis="Dématérialiser et sécuriser l'accès aux dossiers du FDCT.",
        solution="Numérisation, classement et indexation des documents avec mise en place d'un système d'archivage électronique sécurisé.",
        resultat="Facilitation de la consultation et de l'exploitation des dossiers archivés en toute sécurité.",
    ),
    dict(
        nom_client="PUDTR",
        intitule="Mise en place d'un système d'archivage physique et électronique et d'un manuel de référentiel de gestion des archives (PUDTR)",
        annee_execution="2024",
        categorie=numerisation,
        defis="Structurer et sécuriser la gestion des archives physiques et électroniques dans le cadre du PUDTR.",
        solution="Analyse des fonds existants, élaboration d'un plan de classement et d'un manuel de référentiel de gestion des archives.",
        resultat="Mise en place d'un dispositif de sécurisation et de sauvegarde des archives électroniques.",
    ),
    dict(
        nom_client="Centre de Gestion des Cités (CEGECI)",
        intitule="Numérisation des archives du Centre de Gestion des Cités (CEGECI) pour la période 2010-2021",
        annee_execution="2022 - 2024",
        categorie=numerisation,
        defis="Sécuriser et faciliter l'accès aux archives physiques du CEGECI couvrant la période 2010-2021.",
        solution="Tri, numérisation, contrôle qualité, classement et indexation des documents d'archives dans un système d'archivage électronique.",
        resultat="Sécurisation, sauvegarde et facilitation de la recherche et de la consultation des archives.",
    ),
    dict(
        nom_client="Institut Géographique du Burkina (IGB)",
        intitule="Mise en place et mise à jour de logiciels au profit de l'Institut Géographique du Burkina",
        annee_execution="2022 - 2024",
        categorie=genie_logiciel,
        defis="Fiabiliser et faire évoluer les logiciels utilisés par l'IGB.",
        solution="Installation, configuration, mise à jour et paramétrage des logiciels, avec correction des anomalies techniques.",
        resultat="Amélioration des performances et de la fiabilité des applications, avec formation des utilisateurs de l'IGB.",
    ),
]

created_count = 0
for ref in REFERENCES:
    categorie = ref.pop("categorie")
    obj, created = Projet.objects.get_or_create(
        nom_client=ref["nom_client"],
        annee_execution=ref["annee_execution"],
        defaults=dict(
            intitule=f"<p>{ref['intitule']}</p>",
            defis=ref["defis"],
            solution=ref["solution"],
            resultat=ref["resultat"],
            categorie=categorie,
        ),
    )
    if created:
        created_count += 1
        print(f"Cree: {obj.nom_client}")
    else:
        print(f"Deja present, ignore: {obj.nom_client}")

print(f"\nTotal cree: {created_count} / {len(REFERENCES)}")
print(f"Total Projet en base: {Projet.objects.count()}")
