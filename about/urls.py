from django.urls import path
from about import views

urlpatterns = [
    path('qui__somme__nous/', views.about, name='about'),
]
