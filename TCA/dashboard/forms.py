from django import forms
from usuarios.models import Registro, Acciones,  Area, Mensaje
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
import re
from datetime import datetime

class RegistroConAccionesYPruebasForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['claveAcuerdo','fecha_inicio', 'fecha_termino', 'rubro', 'area', 'periodo',]
        labels = {
            'area': 'OR',
        }    

    accion1_area2 = forms.ModelMultipleChoiceField(queryset=Area.objects.all(), label="Áreas Responsables")
    accion1_descripcion = forms.CharField(widget=forms.Textarea, label="Descripción")
    accion1_antecedente = forms.CharField(widget=forms.Textarea, label="Antecedente")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = Area.objects.filter(idArea__lte=32) 

class RegistroConAccionesFORM(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['claveAcuerdo', 'fecha_inicio', 'fecha_termino', 'rubro', 'area', 'estado', 'porcentaje_avance', 'periodo',]
        labels = {
            'claveAcuerdo': 'Clave de Acuerdo',
            'area': 'OR',
            'estado': 'Estatus',
            'porcentaje_avance': 'Porcentaje de Avance'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = Area.objects.filter(idArea__lte=32)
        self.fields['porcentaje_avance'].validators.extend([MaxValueValidator(100), MinValueValidator(0)])

    def clean_claveAcuerdo(self):
        claveAcuerdo = self.cleaned_data.get('claveAcuerdo')
        print(claveAcuerdo)
        pattern = r'^\d{3}/[A-Z]{1,6}/\d{2}/\d{4}$'

        if not re.match(pattern, claveAcuerdo):
            raise ValidationError("La clave del acuerdo debe tener el formato 00/AREA/MES/AÑO.")

        instance_id = self.instance.idRegistro
        if Registro.objects.exclude(idRegistro=instance_id).filter(claveAcuerdo=claveAcuerdo).exists():
            raise forms.ValidationError("Esta clave de acuerdo ya existe.")


        return claveAcuerdo



    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if not fecha_inicio:
            raise ValidationError("La fecha de inicio es obligatoria.")
        
        fecha_inicio_str = fecha_inicio.strftime('%d/%m/%Y')

        if not re.match(r'^\d{2}/\d{2}/\d{4}$', fecha_inicio_str):
            raise ValidationError("La fecha debe tener el formato dd/mm/yyyy.")

        year = int(fecha_inicio_str.split('/')[-1])
        if year < 1000 or year > 9999:
            raise ValidationError("El año debe tener 4 dígitos.")
        
        return fecha_inicio

    def clean_fecha_termino(self):
        fecha_termino = self.cleaned_data.get('fecha_termino')
        if not fecha_termino:
            raise ValidationError("La fecha de término es obligatoria.")
        
        fecha_termino_str = fecha_termino.strftime('%d/%m/%Y')
        
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', fecha_termino_str):
            raise ValidationError("La fecha debe tener el formato dd/mm/yyyy.")

        year = int(fecha_termino_str.split('/')[-1])
        if year < 1000 or year > 9999:
            raise ValidationError("El año debe tener 4 dígitos.")
        
        return fecha_termino


    
class AccionesForm(forms.ModelForm):
    class Meta:
        model = Acciones
        fields = ['area2', 'antecedente','descripcion']
        labels = {
            'area2': 'Áreas Responsables',
        }
        widgets = {
            'antecedente': forms.Textarea(attrs={
                'cols': 30,
                'rows': 7,
            }),
            'descripcion': forms.Textarea(attrs={
                'cols': 30,
                'rows': 7,
            }),
        }

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['texto', 'archivo']
        widgets = {
            'texto': forms.Textarea(attrs={'placeholder': 'Escribe tu mensaje aquí...'}),
        }


class CargarArchivoForm(forms.Form):
    archivo = forms.FileField()