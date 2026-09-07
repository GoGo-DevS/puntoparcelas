from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from core import views as core_views

# 04/09-2026, hoja "06 Redirecciones" de la auditoria de Jorge Urzua: URLs
# viejas (de antes de que las fichas vivieran bajo /catalogo/) que todavia
# rankean en Google y hoy dan 404. Van 301 (permanent=True) al home o a la
# ficha real.
#
# OJO: la "URL nueva sugerida" que trae la hoja de Jorge para 10 de estas
# usa un slug con prefijo "parcela-" (ej. "parcela-bosques-de-frutillar")
# que NO EXISTE en el sitio real -- se verifico contra los 42 slugs reales
# de la hoja "01 Mapping parcelas" y ninguno lo trae. El slug real es el
# mismo de siempre, SIN el prefijo (bosques-de-frutillar). Se corrigio aca;
# no se copio la sugerencia literal.
#
# Las que la propia hoja marca "REVISAR" (categoria vieja, noticias, otras
# 5 sin destino claro) se dejan afuera a proposito -- no se inventa destino
# para una URL que ni el auditor supo a donde mandar.
REDIRECCIONES_301 = [
    ('bosques-de-frutillar',            '/catalogo/bosques-de-frutillar/'),
    ('categoria/parcela',               '/'),
    ('parque-algarrobo',                '/catalogo/parque-algarrobo/'),
    ('vive-santo-domingo',              '/catalogo/vive-santo-domingo/'),
    ('prados-de-frutillar-x-region',    '/catalogo/prados-de-frutillar/'),
    ('vive-ovalle',                     '/catalogo/vive-ovalle/'),
    ('vive-chillan',                    '/catalogo/vive-chillan/'),
    ('hacienda-don-bastian',            '/catalogo/hacienda-don-bastian/'),
    ('fundo-la-quirigua',               '/catalogo/fundo-la-quirigua/'),
    ('vive-osorno-x-region',            '/catalogo/vive-osorno/'),
    ('vive-rupanco-x-region',           '/catalogo/vive-rupanco/'),
    ('brisas-de-bucalemu',              '/catalogo/fundo-santa-rosa/'),
]

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin-panel/', include('panel.urls', namespace='panel')),
    path('robots.txt', core_views.robots_txt),
    path('google7385daff3a5a9bec.html', core_views.google_verify),
    path('sitemap.xml', core_views.sitemap_xml),
    path('site.webmanifest', core_views.manifest_webmanifest, name='manifest'),
    *[path(f'{origen}/', RedirectView.as_view(url=destino, permanent=True))
      for origen, destino in REDIRECCIONES_301],
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
