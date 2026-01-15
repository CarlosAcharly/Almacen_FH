from django import forms
from .models import Dieta

class DietaForm(forms.ModelForm):
    class Meta:
        model = Dieta
        fields = ['nombre', 'etapa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Dieta Gestación Premium'
            }),
            'etapa': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'nombre': 'Nombre de la dieta',
            'etapa': 'Etapa del cerdo'
        }