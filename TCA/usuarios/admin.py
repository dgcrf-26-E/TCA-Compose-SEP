from django.contrib import admin

from .models import Registro, Area, Rubro,  Acciones, UsuarioP, Mensaje, Notificacion, Periodo

class RegistroAdmin(admin.ModelAdmin):
    list_display = ["idRegistro" ,"claveAcuerdo","fecha_inicio", "porcentaje_avance", "estado"]
    list_editable = ["claveAcuerdo", "fecha_inicio", "porcentaje_avance", "estado"]
    list_filter = ["area", "estado"]

class NotificacionAdmin(admin.ModelAdmin):
    list_display = ["user" ,"leido","fecha_leido"]
    list_filter = ["leido", "user"]

admin.site.register(Registro, RegistroAdmin)
admin.site.register(Area)
admin.site.register(Rubro)
admin.site.register(UsuarioP)
admin.site.register(Acciones)
admin.site.register(Mensaje)
admin.site.register(Periodo)
admin.site.register(Notificacion, NotificacionAdmin)