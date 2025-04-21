from django.db import models
from tinymce import models as tinymce_models



class Categorie_Projet(models.Model):
    libelle = models.CharField(max_length=200, null=True, blank=True, verbose_name='Categorie de projet')

    
    def __str__(self):
        return self.libelle

class Projet(models.Model):
    intitule  = tinymce_models.HTMLField(verbose_name='Intitulé de la mission')
    nom_client = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nom ou Raison social du Client')
    annee_execution = models.CharField(max_length=200, null=True, blank=True, verbose_name='Année d\'execution')
    defis = models.TextField(null=True, blank=True, verbose_name='Défis de la mission')
    solution = models.TextField(null=True, blank=True, verbose_name='Solutions apportées')
    resultat = models.TextField(null=True, blank=True, verbose_name='Resultats attendu')
    categorie = models.ForeignKey(Categorie_Projet, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Catégorie de projet")


    def __str__(self):
        return self.nom_client