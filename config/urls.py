from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from core import views as core_views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin-panel/', include('panel.urls', namespace='panel')),
    path('robots.txt', core_views.robots_txt),
    path('sitemap.xml', core_views.sitemap_xml),
    path('', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif not getattr(settings, 'CLOUDINARY_URL', ''):
    # Demo Render/SQLite: sirve uploads locales aun con DEBUG=false.
    # Para produccion real usar CLOUDINARY_URL, porque el filesystem de Render es efimero.
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
