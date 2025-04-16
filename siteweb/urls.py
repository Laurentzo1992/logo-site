from django.urls import path
from siteweb  import views

urlpatterns = [
    path('', views.index, name='index'),
]
