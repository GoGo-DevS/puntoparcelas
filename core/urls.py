from django.urls import path, re_path
from . import views

app_name = 'core'

# 04/09-2026: las 11 regiones reales, para el patron de URL de abajo.
# Con esto exactos slugs (los-lagos, araucania, ...) resuelven a la pagina
# de region; CUALQUIER OTRO slug (todos los de parcela real) sigue cayendo
# en el patron siguiente (parcela_detail), sin ambiguedad ni prefijo extra
# -- la URL queda EXACTA a la que pidio Jorge: /catalogo/los-lagos/, no
# /catalogo/region/los-lagos/.
_REGION_SLUGS = 'los-lagos|araucania|metropolitana|ohiggins|nuble|coquimbo|los-rios|valparaiso|maule|biobio|aysen'

urlpatterns = [
    path('',                views.home,           name='home'),
    path('catalogo/',       views.catalogo,       name='catalogo'),
    re_path(rf'^catalogo/(?P<region_url>{_REGION_SLUGS})/$', views.catalogo, name='catalogo_region'),
    path('catalogo/<slug:slug>/',          views.parcela_detail, name='parcela_detail'),
    path('catalogo/<slug:slug>/geo-pdf/', views.parcela_geo_pdf, name='parcela_geo_pdf'),
    path('contacto/',       views.reserva,        name='reserva'),
    path('links/',          views.links,          name='links'),
]
