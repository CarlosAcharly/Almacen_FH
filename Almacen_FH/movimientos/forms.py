from django import forms
from .models import Entrada, Salida
from .models import Merma

class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        exclude = ('usuario',)
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'toneladas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bultos': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bultos'].required = False
        self.fields['bultos'].initial = 0


class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        exclude = ('usuario',)
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'lugar': forms.Select(attrs={'class': 'form-select'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'toneladas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bultos': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bultos opcional
        self.fields['bultos'].required = False
        self.fields['bultos'].initial = 0

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        kg = cleaned_data.get('kg') or 0
        toneladas = cleaned_data.get('toneladas') or 0
        bultos = cleaned_data.get('bultos') or 0

        # Asegurarnos de que peso_por_bulto no sea None
        peso_por_bulto = getattr(producto, 'peso_por_bulto', 0) or 0

        total_kg = kg + toneladas * 1000 + bultos * peso_por_bulto

        if producto and total_kg > getattr(producto, 'stock_kg', 0):
            raise forms.ValidationError(
                f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_kg} kg"
            )
        return cleaned_data


class MermaForm(forms.ModelForm):
    class Meta:
        model = Merma
        fields = [
            'producto',
            'motivo',
            'descripcion',
            'kg',
            'toneladas',
            'bultos',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }