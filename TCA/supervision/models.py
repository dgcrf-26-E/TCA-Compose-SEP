from django.db import models
from usuarios.models import Rubro, Area, Periodo

class RegistroTemporal(models.Model):
    types_estado = [
        ("1", "En proceso"),
        ("2", "Atendido"),
    ]

    idRegistro = models.AutoField(primary_key=True)
    claveAcuerdo = models.CharField(default="Clave de Acuerdo", max_length=20)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    rubro = models.ManyToManyField(Rubro, related_name='registroRTemporal')
    area = models.ManyToManyField(Area, related_name='registroATemporal')
    estado = models.CharField(max_length=1, choices=types_estado, default="1")
    fecha_finalizacion = models.DateField(default="1970-01-01")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    porcentaje_avance = models.IntegerField(default=0)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Registro Temp: {self.idRegistro}, Clave: {self.claveAcuerdo}"

class AccionesTemporal(models.Model):
    idAccion = models.AutoField(primary_key=True)
    idRegistro = models.ManyToManyField(RegistroTemporal, related_name='accionRTemporal')
    area2 = models.ManyToManyField(Area, related_name='accionA2Temporal')
    antecedente = models.TextField(blank=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Acción Temp: {self.idAccion}, Desc: {self.descripcion}"


class Formulario(models.Model):
    titulo = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    def calcular_calificacion_global(self):
        """
        Calcula la calificación global del formulario,
        promediando las secciones activas ponderadas.
        """
        secciones = self.secciones.filter(activo=True)
        if not secciones.exists():
            return 0

        total_ponderado = 0
        total_pesos = 0
        for seccion in secciones:
            calificacion = seccion.calcular_promedio()
            total_ponderado += calificacion * seccion.ponderacion
            total_pesos += seccion.ponderacion

        return round(total_ponderado / total_pesos, 2) if total_pesos > 0 else 0


class Seccion(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name="secciones")
    titulo = models.CharField(max_length=255)
    ponderacion = models.FloatField(default=1.0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({self.formulario.titulo})"

    def calcular_promedio(self):
        subsecciones = self.subsecciones.filter(activo=True)
        if not subsecciones.exists():
            return 0

        total_ponderado = 0
        total_pesos = 0
        for sub in subsecciones:
            calificacion = sub.calcular_promedio()
            total_ponderado += calificacion * sub.ponderacion
            total_pesos += sub.ponderacion

        return round(total_ponderado / total_pesos, 2) if total_pesos > 0 else 0


class SubSeccion(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name="subsecciones")
    titulo = models.CharField(max_length=255)
    ponderacion = models.FloatField(default=1.0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({self.seccion.titulo})"

    def calcular_promedio(self):
        preguntas = self.preguntas.filter(activo=True)
        if not preguntas.exists():
            return 0

        total = 0
        count = 0
        for pregunta in preguntas:
            cal = pregunta.calcular_calificacion()
            if cal is not None:
                total += cal
                count += 1

        return round(total / count, 2) if count > 0 else 0


class Pregunta(models.Model):
    TIPO_PREGUNTA_CHOICES = [
        ("SI_NO", "Sí o No + Comentarios"),
        ("VALORACION", "Bueno / Regular / Malo + Comentarios"),
        ("COMENTARIO", "Solo Comentarios"),
    ]

    subseccion = models.ForeignKey(SubSeccion, on_delete=models.CASCADE, related_name="preguntas")
    texto = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_PREGUNTA_CHOICES)
    activo = models.BooleanField(default=True)
    ponderacion = models.FloatField(default=1.0)
    pregunta_padre = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="preguntas_hijas"
    )

    def __str__(self):
        return self.texto

    def calcular_calificacion(self):
        """
        Calcula una calificación estimada en base al tipo de pregunta.
        Nota: en la práctica se calcularía con las respuestas.
        """
        # Solo como placeholder para pruebas
        if self.tipo == "SI_NO":
            return 1
        elif self.tipo == "VALORACION":
            return 1
        elif self.tipo == "COMENTARIO":
            return None
        return None


# class RespuestaFormulario(models.Model):
#     formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name="respuestas")
#     fecha = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Respuesta #{self.id} - {self.formulario.titulo}"
    
class RespuestaFormulario(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name="respuestas")
    oficina = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=100, blank=True, null=True)

    def calcular_calificacion(self):
        """
        Calcula la calificación global del formulario,
        promediando secciones ponderadas.
        """
        secciones = self.formulario.secciones.filter(activo=True)
        if not secciones.exists():
            return 0

        total, peso_total = 0, 0
        for seccion in secciones:
            calificacion = self.calcular_calificacion_seccion(seccion)
            total += calificacion * seccion.ponderacion
            peso_total += seccion.ponderacion

        return round(total / peso_total, 2) if peso_total > 0 else 0

    def calcular_calificacion_seccion(self, seccion):
        """
        Calcula el promedio de una sección considerando subsecciones.
        """
        subsecciones = seccion.subsecciones.filter(activo=True)
        if not subsecciones.exists():
            return 0

        total, peso_total = 0, 0
        for sub in subsecciones:
            calificacion = self.calcular_calificacion_subseccion(sub)
            total += calificacion * sub.ponderacion
            peso_total += sub.ponderacion

        return round(total / peso_total, 2) if peso_total > 0 else 0

    def calcular_calificacion_subseccion(self, subseccion):
        """
        Calcula el promedio de preguntas habilitadas en una subsección.
        """
        respuestas_preguntas = self.respuestas.filter(
            pregunta__subseccion=subseccion, habilitada=True
        )
        if not respuestas_preguntas.exists():
            return 0

        valores = []
        for r in respuestas_preguntas:
            valor = self._mapear_valor(r)
            if valor is not None:
                valores.append(valor)

        return round(sum(valores) / len(valores), 2) if valores else 0

    def _mapear_valor(self, respuesta):
        """
        Convierte la respuesta en un valor numérico de 0 a 10.
        Si solo tiene comentario (sin valor), cuenta como 10.
        """
        if respuesta.valor is None or respuesta.valor.strip() == "":
            # 👇 Solo comentario, se toma como "correcto"
            return 10  

        # Tipo Sí/No → Sí=10, No=0
        if respuesta.valor.lower() in ["sí", "si", "yes"]:
            return 10
        elif respuesta.valor.lower() in ["no"]:
            return 0

        # Tipo Bueno/Regular/Malo
        mapping = {
            "bueno": 10,
            "regular": 5,
            "malo": 0,
        }
        if respuesta.valor.lower() in mapping:
            return mapping[respuesta.valor.lower()]

        return 10  # fallback: cualquier otro texto se toma como válido = 10


class RespuestaPregunta(models.Model):
    respuesta_formulario = models.ForeignKey(
        RespuestaFormulario, on_delete=models.CASCADE, related_name="respuestas"
    )
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    valor = models.CharField(max_length=20, blank=True, null=True)  # sí/no/bueno/regular/malo
    comentario = models.TextField(blank=True, null=True)
    habilitada = models.BooleanField(default=True)  # 👈 Nuevo campo

    def __str__(self):
        return f"Respuesta a {self.pregunta.texto} ({'habilitada' if self.habilitada else 'NO aplica'})"


class ReporteGenerado(models.Model):
    idReporte = models.AutoField(primary_key=True)
    clave = models.CharField(default="Clave", max_length=20)
    archivo = models.FileField(upload_to='words/')
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    firmado = models.BooleanField(default=False)
    archivo_firmado = models.FileField(upload_to='words/firmados/', null=True, blank=True)
    periodo = models.ForeignKey(Periodo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Reporte {self.idReporte} - {self.fecha_generacion.strftime('%Y-%m-%d %H:%M')}"

