from django import forms
from .models import (
    Categoria, Producto, Proveedor,
    Cliente, Lugar, Chofer, UnidadTransporte
)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'categoria',
            'descripcion',
            #'peso_bulto_kg',
            'stock_kg',
            #'stock_minimo_kg',
            'activo'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'


class LugarForm(forms.ModelForm):
    class Meta:
        model = Lugar
        fields = '__all__'


class ChoferForm(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = '__all__'


class UnidadForm(forms.ModelForm):
    class Meta:
        model = UnidadTransporte
        fields = '__all__'
