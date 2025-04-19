from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from tinymce.models import HTMLField
from tinymce import models as tinymce_models


class About_Us(models.Model):
    fichier = models.FileField(upload_to='partenaire_img/', null=True, blank=True, verbose_name="Les images Partenaire de logo services")
    contenu = tinymce_models.HTMLField(blank=True, null=True, verbose_name="Description")
    
    
    
    
class Contact(models.Model):
    adresse = tinymce_models.HTMLField(verbose_name="Adresse")
    email = models.EmailField(unique=True, verbose_name='Email')
    telephone = models.CharField(max_length=100, null=False, blank=False, verbose_name='Téléphone')
    heure_ouverture = tinymce_models.HTMLField()
    
    
    def __str__(self):
        return self.email
    
