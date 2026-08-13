from django import forms
from django.contrib.auth.forms import AuthenticationForm

from core.models import Consulta, FotoParcela, Parcela, SiteConfig, Testimonio


class PanelLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Usuario',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Contraseña',
    }))


class ParcelaForm(forms.ModelForm):
    class Meta:
        model = Parcela
        fields = [
            'nombre', 'region', 'sector', 'precio', 'moneda', 'superficie',
            'descripcion', 'destacada', 'estado',
            'tiene_luz', 'tiene_agua', 'tiene_acceso', 'vista_privilegiada',
            'tiene_cercado', 'tiene_porton', 'es_turistico', 'bosque_nativo', 'rol_propio',
            'video_url', 'mapa_url', 'mapa_embed_url', 'geo_pdf', 'imagen_credito',
        ]
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'form-control'}),
            'region':      forms.Select(attrs={'class': 'form-select'}),
            'sector':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Colina, Pirque...'}),
            'precio':      forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número sin puntos'}),
            'moneda':      forms.Select(attrs={'class': 'form-select'}),
            'superficie':  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Superficie en m²'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado':      forms.Select(attrs={'class': 'form-select'}),
            'video_url':      forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtu.be/...'}),
            'mapa_url':       forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://maps.app.goo.gl/...'}),
            'mapa_embed_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.google.com/maps/embed?pb=...'}),
            'geo_pdf':        forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'imagen_credito': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class FotoParcelaForm(forms.ModelForm):
    class Meta:
        model = FotoParcela
        fields = ['imagen', 'principal', 'orden']
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px'}),
        }


class TestimonioForm(forms.ModelForm):
    class Meta:
        model = Testimonio
        fields = ['nombre', 'profesion', 'ciudad', 'texto', 'estrellas', 'activo', 'orden']
        widgets = {
            'nombre':    forms.TextInput(attrs={'class': 'form-control'}),
            'profesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Inversionista'}),
            'ciudad':    forms.TextInput(attrs={'class': 'form-control'}),
            'texto':     forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estrellas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'orden':     forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ConsultaEstadoForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['estado', 'notas']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MedicionForm(forms.ModelForm):
    """Los ID de medicion los pega Leonardo, con SUS cuentas.

    No van en el codigo a proposito: si se hardcodean, las cuentas terminan
    siendo de GoGoDevS y el cliente queda amarrado -- mismo criterio que con el
    dominio. Dejar un campo vacio APAGA esa etiqueta, no la deja a medias.
    """

    class Meta:
        model = SiteConfig
        fields = ['ga4_id', 'meta_pixel_id', 'meta_verificacion', 'google_verificacion']
        widgets = {
            'ga4_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'G-ABC1234567'}),
            'meta_pixel_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890123456'}),
            'meta_verificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lo entrega Meta'}),
            'google_verificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
        }
