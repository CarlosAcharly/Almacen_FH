from django import forms
from django.forms import inlineformset_factory
from .models import (
    Entrada, Salida, Merma,
    Movimiento, MovimientoDetalle
)
from catalogos.models import Producto

# =========================
# ENTRADAS
# =========================
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
        # Bultos opcional
        if 'bultos' in self.fields:
            self.fields['bultos'].required = False
            self.fields['bultos'].initial = 0

        producto = self.initial.get('producto') or getattr(self.instance, 'producto', None)
        if producto and producto.categoria.nombre == "Dietas":
            self.fields.pop('bultos', None)
            self.fields.pop('toneladas', None)


# =========================
# SALIDAS
# =========================
class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        exclude = ('usuario',)
        widgets = {
            'producto': forms.Select(attrs={'class': 'glass-input'}),
            'cliente': forms.Select(attrs={'class': 'glass-input'}),
            'lugar': forms.Select(attrs={'class': 'glass-input'}),
            'kg': forms.NumberInput(attrs={'class': 'glass-input', 'step': '0.01', 'min': '0'}),
            'toneladas': forms.NumberInput(attrs={'class': 'glass-input', 'step': '0.01', 'min': '0'}),
            'bultos': forms.NumberInput(attrs={'class': 'glass-input', 'step': '1', 'min': '0'}),
            'tipo': forms.Select(attrs={'class': 'glass-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'bultos' in self.fields:
            self.fields['bultos'].required = False
            self.fields['bultos'].initial = 0

        producto = self.initial.get('producto') or getattr(self.instance, 'producto', None)
        if producto and producto.categoria.nombre == "Dietas":
            self.fields.pop('bultos', None)
            self.fields.pop('toneladas', None)

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        if not producto:
            return cleaned_data

        kg = cleaned_data.get('kg') or 0
        toneladas = cleaned_data.get('toneladas') or 0
        bultos = cleaned_data.get('bultos') or 0

        if producto.categoria.nombre == "Dietas":
            total_kg = kg
        else:
            peso_por_bulto = producto.peso_por_bulto or 0
            total_kg = kg + (toneladas * 1000) + (bultos * peso_por_bulto)

        if total_kg > producto.stock_kg:
            raise forms.ValidationError(
                f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_kg} kg"
            )

        return cleaned_data


# =========================
# MERMAS
# =========================
class MermaForm(forms.ModelForm):
    class Meta:
        model = Merma
        fields = ['producto', 'motivo', 'descripcion', 'kg', 'toneladas', 'bultos']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'toneladas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bultos': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'bultos' in self.fields:
            self.fields['bultos'].required = False
            self.fields['bultos'].initial = 0


# =========================
# MOVIMIENTO Y DETALLES
# =========================
class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['tipo', 'cliente', 'lugar', 'chofer', 'unidad']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'lugar': forms.Select(attrs={'class': 'form-select'}),
            'chofer': forms.Select(attrs={'class': 'form-select'}),
            'unidad': forms.Select(attrs={'class': 'form-select'}),
        }


class MovimientoDetalleForm(forms.ModelForm):
    class Meta:
        model = MovimientoDetalle
        fields = ['producto', 'kg', 'toneladas', 'bultos']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'toneladas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bultos': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }

MovimientoDetalleFormSet = inlineformset_factory(
    Movimiento,
    MovimientoDetalle,
    form=MovimientoDetalleForm,
    extra=1,
    can_delete=True
)
