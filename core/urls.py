from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',                views.home,           name='home'),
    path('catalogo/',       views.catalogo,       name='catalogo'),
    path('catalogo/<slug:slug>/', views.parcela_detail, name='parcela_detail'),
    path('contacto/',       views.reserva,        name='reserva'),
    path('links/',          views.links,          name='links'),
]
