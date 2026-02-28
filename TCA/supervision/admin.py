from django.contrib import admin
from .models import (
    Formulario,
    Seccion,
    SubSeccion,
    Pregunta,
    RespuestaFormulario,
    RespuestaPregunta,
    RegistroTemporal,
    AccionesTemporal,
    ReporteGenerado,
)


class PreguntaInline(admin.TabularInline):
    model = Pregunta
    extra = 1


class SubSeccionInline(admin.StackedInline):
    model = SubSeccion
    extra = 1
    show_change_link = True


class SeccionInline(admin.StackedInline):
    model = Seccion
    extra = 1
    show_change_link = True


@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "calificacion_global")
    inlines = [SeccionInline]

    def calificacion_global(self, obj):
        return obj.calcular_calificacion_global()


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "formulario", "ponderacion", "activo", "promedio")
    inlines = [SubSeccionInline]

    def promedio(self, obj):
        return obj.calcular_promedio()


@admin.register(SubSeccion)
class SubSeccionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "seccion", "ponderacion", "activo", "promedio")
    inlines = [PreguntaInline]

    def promedio(self, obj):
        return obj.calcular_promedio()


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("texto", "tipo", "subseccion", "activo", "padre")
    list_filter = ("tipo", "activo")
    search_fields = ("texto",)

    def padre(self, obj):
        return obj.pregunta_padre.texto if obj.pregunta_padre else "-"


class RespuestaPreguntaInline(admin.TabularInline):
    model = RespuestaPregunta
    extra = 1


@admin.register(RespuestaFormulario)
class RespuestaFormularioAdmin(admin.ModelAdmin):
    list_display = ("id", "formulario", "fecha")
    inlines = [RespuestaPreguntaInline]


@admin.register(RespuestaPregunta)
class RespuestaPreguntaAdmin(admin.ModelAdmin):
    list_display = ("pregunta", "valor", "comentario", "habilitada")
    list_filter = ("valor", "habilitada")
    search_fields = ("comentario",)


## -----------------------------------------------  ##########
## -----------------------------------------------  ##########

@admin.register(AccionesTemporal)
class AccionesTemporalAdmin(admin.ModelAdmin):
    list_display = ("idAccion", "descripcion", "antecedente")

@admin.register(RegistroTemporal)
class RegistroTemporalAdmin(admin.ModelAdmin):
    list_display = ("idRegistro", "claveAcuerdo", "fecha_inicio", "fecha_termino", "estado")

@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ("idReporte", "clave", "fecha_generacion", "firmado", "periodo")
    list_filter = ("firmado", "periodo")
