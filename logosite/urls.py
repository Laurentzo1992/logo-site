from django.contrib import admin
from django.urls import path, include
from  django.conf.urls.static import  static
from  django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('rest', include('rest_framework.urls', namespace='rest_framework')),
	path('', include('siteweb.urls')),
    path('', include('about.urls')),
    path('', include('blog.urls')),
    path('catalog', include('catalog.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)