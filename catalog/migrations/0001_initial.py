# Generated by Django 5.1.6 on 2025-04-21 16:22

import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie_Projet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(blank=True, max_length=200, null=True, verbose_name='Categorie de projet')),
            ],
        ),
        migrations.CreateModel(
            name='Projet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intitule', tinymce.models.HTMLField(verbose_name='Intitulé de la mission')),
                ('nom_client', models.CharField(blank=True, max_length=200, null=True, verbose_name='Categorie de projet')),
                ('annee_execution', models.CharField(blank=True, max_length=200, null=True, verbose_name="Année d'execution")),
            ],
        ),
    ]
