from django import forms
from .models import Consulta, REGIONES


class ConsultaForm(forms.ModelForm):
    region_interes = forms.ChoiceField(
        choices=[('', 'Seleccionar región')] + list(REGIONES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    monto_rango = forms.ChoiceField(
        choices=[('', 'Seleccionar rango')] + list(Consulta.MONTO_RANGO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    como_nos_conociste = forms.ChoiceField(
        choices=[('', 'Seleccionar opción')] + list(Consulta.COMO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Consulta
        fields = [
            'nombre', 'email', 'telefono', 'region_interes',
            'monto_rango', 'como_nos_conociste', 'mensaje', 'parcela',
        ]
        widgets = {
            'nombre':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email':    forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@email.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 XXXX XXXX'}),
            'mensaje':  forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '¿Qué buscas? ¿Para qué uso? ¿Alguna duda?'}),
            'parcela':  forms.HiddenInput(),
        }
