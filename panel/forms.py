from django import forms
from django.contrib.auth.forms import AuthenticationForm

from core.models import Consulta, FotoParcela, Parcela, Testimonio


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
            'nombre', 'region', 'sector', 'precio', 'superficie',
            'descripcion', 'destacada', 'estado',
            'tiene_luz', 'tiene_agua', 'tiene_acceso', 'vista_privilegiada',
            'tiene_cercado', 'tiene_porton', 'es_turistico', 'bosque_nativo', 'rol_propio',
        ]
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'form-control'}),
            'region':      forms.Select(attrs={'class': 'form-select'}),
            'sector':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Colina, Pirque...'}),
            'precio':      forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio en CLP'}),
            'superficie':  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Superficie en m²'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado':      forms.Select(attrs={'class': 'form-select'}),
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
