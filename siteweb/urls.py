from django.urls import path
from siteweb  import views

urlpatterns = [
    path('', views.index, name='index'),
    path("api/services/", views.api_services),
    path('api/subscribe_newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
]
