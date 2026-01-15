# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UsuarioRegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo electrónico'
    }))
    
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono'
        })
    )
    
    rol = forms.ChoiceField(
        choices=Usuario.ROLES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Observaciones',
            'rows': 3
        })
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'rol', 'observaciones',
            'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets de password para que tengan la misma clase
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está registrado')
        return username

    def save(self, commit=True, creado_por=None):
        usuario = super().save(commit=False)
        if creado_por:
            usuario.creado_por = creado_por
        if commit:
            usuario.save()
        return usuario


class UsuarioEditarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email', 'telefono',
            'rol', 'estado', 'observaciones'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class PerfilEditarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CambiarContrasenaForm(forms.Form):
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')
        
        if nueva_contrasena and confirmar_contrasena:
            if nueva_contrasena != confirmar_contrasena:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data