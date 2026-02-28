from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registro, Notificacion, UsuarioP, Acciones

@receiver(post_save, sender=Acciones)
def notificar_creacion_o_actualizacion_accion(sender, instance, created, **kwargs):
    pass
    # print(f"registro {instance.idAccion}")
    # registroI = Registro.objects.filter(idRegistro=instance.idRegistro).first()

    # if created:
    #     mensaje = f"Se ha creado un nuevo acuerdo: {registroI.claveAcuerdo} en la {registroI.area.name}."
    # else:
    #     mensaje = f"Se ha actualizado el acuerdo: {registroI.claveAcuerdo}"

    # # Obtener todos los usuarios del área asociada
    # print(instance.area2)

    # usuarios_del_area = UsuarioP.objects.filter(area__in=instance.area2)

    # # Crear una notificación para cada usuario del área
    # for usuarioC in usuarios_del_area:
    #     Notificacion.objects.create(
    #         user=usuarioC.user,
    #         mensaje=mensaje
    #     )