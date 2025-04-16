from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from tinymce.models import HTMLField
from tinymce import models as tinymce_models


class About_Us(models.Model):
    titre = models.CharField(max_length=200, blank=True, null=True, verbose_name="titre")
    contenu = tinymce_models.HTMLField(blank=True, null=True, verbose_name="Description")
    
    def __str__(self):
        return self.titre