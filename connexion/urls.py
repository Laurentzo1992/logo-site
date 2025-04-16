from django.urls import path, include
from connexion.views import LoginViewset
from rest_framework import routers



router = routers.SimpleRouter()
router.register('users', LoginViewset, basename='users')


urlpatterns = [
    path('api/', include(router.urls)),
]