from django.db import models
from tinymce import models as tinymce_models
    
    

class Services(models.Model):
    libelle = models.CharField(max_length=100, null=False, blank=False, verbose_name='Nom du Services')
    description = tinymce_models.HTMLField()
    icon = models.CharField(max_length=100, null=True, blank=True)
    
    
    def __str__(self):
        return self.libelle
    
    
    
class Newletter_Email(models.Model):
    email = models.EmailField(verbose_name='Nom du Services')

    def __str__(self):
        return self.email
    
    
     
