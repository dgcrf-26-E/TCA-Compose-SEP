from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User 
from datetime import date
from datetime import datetime
# from twilio.rest import Client
# import os
# from dotenv import load_dotenv

# load_dotenv()

import os
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Area(models.Model):
    idArea = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=150)
    name = models.CharField(max_length=300, default="Area 1")

    def __str__(self):
        return f"{self.idArea},{self.nickname},"


class Rubro(models.Model):
    idRubro = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.idRubro}, {self.tipo}"
    
class Periodo(models.Model):
    desc = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id}, {self.desc}"


class Registro(models.Model):
    types_estado = [
        ("1", "En proceso"),
        ("2", "Atendido"),
    ]

    idRegistro = models.AutoField(primary_key=True)
    claveAcuerdo = models.CharField(default="Clave de Acuerdo", max_length=20)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    rubro = models.ManyToManyField(Rubro, related_name='registroR')
    area = models.ManyToManyField(Area, related_name='registroA')
    estado = models.CharField(max_length=1, choices=types_estado, default="1")
    fecha_finalizacion = models.DateField(default="1970-01-01")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    porcentaje_avance = models.IntegerField(default=0)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)

    def __str__(self):
        # return f"hola"
        # return f"Registro: {self.idRegistro}, Clave de Acuerdo: {self.claveAcuerdo}, Fecha de inicio: {self.fecha_inicio}, Fecha de término: {self.fecha_termino}, Rubro: , OR: , Estatus: {self.get_estado_display()}"
        # return f"Registro: {self.idRegistro}, Clave de Acuerdo: {self.claveAcuerdo}, Fecha de inicio: {self.fecha_inicio}, Fecha de término: {self.fecha_termino}, Rubro: {', '.join([rubro.tipo for rubro in self.rubro.all()])}, OR: {', '.join([area.nickname for area in self.area.all()])}, Estatus: {self.get_estado_display()}"
        return f"Registro: {self.idRegistro}, Clave de Acuerdo: {self.claveAcuerdo}, Periodo: {self.periodo.desc}"

class Notificacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    registro_id = models.IntegerField(default=1)
    mensaje = models.TextField(null=True, blank=True)
    leido = models.BooleanField(default=False)
    fecha_leido = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Notificación para {self.user.username} sobre {self.mensaje}"
    
class Acciones(models.Model):
    idAccion = models.AutoField(primary_key=True)
    idRegistro = models.ManyToManyField(Registro, related_name='accionR')
    area2 = models.ManyToManyField(Area, related_name='accionA2')
    antecedente = models.TextField(blank=True)
    descripcion = models.TextField()

    def __str__(self):
        return "Acción: {accion}, Registros: {datosRegistro}, Área 2: {area2}, Descripción: {descripcionI}".format(
            accion= self.idAccion,
            datosRegistro= ', '.join([ str([registro.idRegistro, registro.claveAcuerdo ,  registro.rubro.all()[0].tipo])  for registro in self.idRegistro.all()]),
            area2= ', '.join([area.nickname for area in self.area2.all()]),
            descripcionI= self.descripcion,
        )
        # return f"Acción: {self.idAccion}, Registros: {', '.join([ str([registro.idRegistro, str(registro.rubro.all()[0].tipo)])  for registro in self.idRegistro.all()])}, Área 2: {', '.join([area.nickname for area in self.area2.all()])}, Descripción: {self.descripcion}"


class UsuarioP(models.Model):
    types_ORS = [
        ("1", "OR AGS"), ("2", "OR BC"), ("3", "OR BCS"), ("4", "OR CAMP"), ("5", "OR COAH"),
        ("6", "OR COL"), ("7", "OR CHIS"), ("8", "OR CHIH"), ("9", "OR CDMX"), ("10", "OR DGO"),
        ("11", "OR GTO"), ("12", "OR GRO"), ("13", "OR HGO"), ("14", "OR JAL"), ("15", "OR EDOMEX"),
        ("16", "OR MICH"), ("17", "OR MOR"), ("18", "OR NAY"), ("19", "OR NL"), ("20", "OR OAX"),
        ("21", "OR PUE"), ("22", "OR QRO"), ("23", "OR QROO"), ("24", "OR SLP"), ("25", "OR SIN"),
        ("26", "OR SON"), ("27", "OR TAB"), ("28", "OR TAMPS"), ("29", "OR TLX"), ("30", "OR VER"),
        ("31", "OR YUC"), ("32", "OR ZAC"), ("33", "OC"), ("34", "OSCJ"), ("35", "CECC"), ("36", "DCS"), ("37", "DGA"), ("38", "DGCOR"), ("39", "DGCVM"), ("40", "DGPMV"),("41", "DGRAM"),("42", "DGTIC"),("43", "AICMX"),("44", "DC"),
    ]


    types_user = [
        ("1" , "Administrador"),
        ("2", "Editor"),
    ]
    idUser = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, related_name="usuarioP", on_delete=models.CASCADE, default=1)
    nickname = models.CharField(max_length = 20)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200)
    # password = models.CharField(max_length=250)
    OR = models.CharField(max_length=2, choices=types_ORS, default="9")
    tipo = models.CharField(max_length=1, choices=types_user, default="3")
    # Ntelefono = models.CharField(max_length=14, default="+5215637792161")
    
    def save(self, *args, **kwargs):
        # print(self.Ntelefono)
        # account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        # auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        # from_='whatsapp:+14155238886',

        # body = 'DGCOR te ha añadido al TCA, visita tca.dgcor.com',
        # to=f'whatsapp:{self.Ntelefono}'
        
        # )

        # print(message)
        super(UsuarioP, self).save(*args, **kwargs)

    def __str__(self):
        return  " {id}, {nickname}, {state}, {type}".format(id = self.idUser, nickname = self.nickname, state = self.OR, type = self.tipo)
    

class Mensaje(models.Model):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name='mensajes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    archivo = models.FileField(upload_to='mensajes/', blank=True, null=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_envio} - {self.registro} - {self.texto} - {self.archivo}"
    
@receiver(post_delete, sender=Mensaje)
def eliminar_archivo_mensaje(sender, instance, **kwargs):
    if instance.archivo:
        if os.path.isfile(instance.archivo.path):
            os.remove(instance.archivo.path)