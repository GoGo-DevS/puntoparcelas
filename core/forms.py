from django import forms
from .models import Consulta, REGIONES


class ConsultaForm(forms.ModelForm):
    region_interes = forms.ChoiceField(
        choices=[('', 'Cualquier región')] + list(REGIONES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    monto_disponible = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 40000000',
        }),
    )

    class Meta:
        model = Consulta
        fields = ['nombre', 'email', 'telefono', 'region_interes', 'monto_disponible', 'mensaje', 'parcela']
        widgets = {
            'nombre':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email':    forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@email.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 XXXX XXXX'}),
            'mensaje':  forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '¿Qué buscas? ¿Para qué uso? ¿Tiene alguna duda?'}),
            'parcela':  forms.HiddenInput(),
        }
