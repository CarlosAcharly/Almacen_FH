from django import forms
from .models import (
    Categoria, Producto, Proveedor,
    Cliente, Lugar, Chofer, UnidadTransporte
)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'Nombre de la categoría'
            })
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'categoria',
            'descripcion',
            'stock_kg',
            'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'glass-input'}),
            'categoria': forms.Select(attrs={'class': 'glass-input'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'glass-input',
                'rows': 3
            }),
            'stock_kg': forms.NumberInput(attrs={'class': 'glass-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control glass-input'
            })


class LugarForm(forms.ModelForm):
    class Meta:
        model = Lugar
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control glass-input'
            })


class ChoferForm(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control glass-input'
            })



from django import forms
from .models import UnidadTransporte

class UnidadForm(forms.ModelForm):
    class Meta:
        model = UnidadTransporte
        fields = ['marca', 'placa', 'color', 'activa']
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

