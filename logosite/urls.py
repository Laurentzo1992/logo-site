from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path('rest', include('rest_framework.urls', namespace='rest_framework')),
	path('', include('siteweb.urls')),
    path('', include('about.urls')),
    path('', include('blog.urls')),
    path('', include('catalog.urls')),
    path('tinymce/', include('tinymce.urls')),
    # Fichiers statiques attendus à la racine du site par les moteurs de
    # recherche/crawlers (pas dans /static/, donc pas servis autrement).
    path('robots.txt', serve, {'document_root': settings.BASE_DIR, 'path': 'robots.txt'}),
    path('sitemap.xml', serve, {'document_root': settings.BASE_DIR, 'path': 'sitemap.xml'}),
]

# Served unconditionally (not gated behind DEBUG) since this deployment has
# no separate media host/CDN in front of it.
urlpatterns += [
    re_path(
        r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]