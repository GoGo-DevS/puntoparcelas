from django.contrib import admin
from .models import Consulta, FotoParcela, Parcela, Testimonio


class FotoParcelaInline(admin.TabularInline):
    model = FotoParcela
    extra = 1


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'region', 'precio_clp', 'superficie_display', 'estado', 'destacada']
    list_filter   = ['region', 'estado', 'destacada']
    search_fields = ['nombre', 'sector']
    inlines       = [FotoParcelaInline]
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'estrellas', 'es_placeholder', 'activo', 'orden']
    list_editable = ['activo', 'orden']


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'telefono', 'email', 'region_interes', 'estado', 'creado']
    list_filter   = ['estado', 'region_interes']
    search_fields = ['nombre', 'telefono', 'email']
    readonly_fields = ['creado']
