from django import forms
from django.contrib.auth.models import User
from usuarios.models import UsuarioP, Rubro, Area

class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña:',
        help_text='Min. 10 caracteres',
        widget=forms.PasswordInput, 
        required=False)

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user

class UsuarioPForm(forms.ModelForm):
    class Meta:
        model = UsuarioP
        fields = ['nombre', 'apellido', 'OR','tipo']
    
class AccessKeyForm(forms.Form):
    key = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
        label="Clave de acceso"
    )

class UsuarioPForm(forms.ModelForm):
    class Meta:
        model = UsuarioP
        fields = ['nombre', 'apellido', 'OR','tipo']

class RubroForm(forms.ModelForm):
    class Meta:
        model = Rubro
        fields = ['idRubro', 'tipo']

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['idArea', 'nickname', 'name']
        labels = {
            'nickname': 'Nombre Corto del Area',
            'name': 'Nombre completo del Area',
        }
        help_texts = {
            'nickname': 'Ej. - OR AGS',
            'name': 'Ej. - OR AGUASCALIENTES',
        }