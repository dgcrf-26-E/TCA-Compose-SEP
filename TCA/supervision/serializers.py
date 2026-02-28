from rest_framework import serializers
from .models import Formulario, Seccion, SubSeccion, Pregunta
from .models import RespuestaFormulario, RespuestaPregunta, RegistroTemporal, AccionesTemporal, ReporteGenerado
from usuarios.models import Area, Rubro, Periodo


class PreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pregunta
        fields = ["id", "texto", "tipo", "ponderacion", "activo", "pregunta_padre"]


class SubseccionSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True)

    class Meta:
        model = SubSeccion
        fields = ["id", "titulo", "ponderacion", "activo", "preguntas"]

    def create(self, validated_data):
        preguntas_data = validated_data.pop("preguntas", [])
        subseccion = SubSeccion.objects.create(**validated_data)
        for pregunta_data in preguntas_data:
            Pregunta.objects.create(subseccion=subseccion, **pregunta_data)
        return subseccion

    def update(self, instance, validated_data):
        preguntas_data = validated_data.pop("preguntas", [])
        instance.titulo = validated_data.get("titulo", instance.titulo)
        instance.ponderador = validated_data.get("ponderador", instance.ponderador)
        instance.activo = validated_data.get("activo", instance.activo)
        instance.save()

        # Limpiar preguntas existentes y recrearlas
        instance.preguntas.all().delete()
        for pregunta_data in preguntas_data:
            Pregunta.objects.create(subseccion=instance, **pregunta_data)
        return instance


class SeccionSerializer(serializers.ModelSerializer):
    subsecciones = SubseccionSerializer(many=True)

    class Meta:
        model = Seccion
        fields = ["id", "titulo", "ponderacion", "activo", "subsecciones"]

    def create(self, validated_data):
        subsecciones_data = validated_data.pop("subsecciones", [])
        seccion = Seccion.objects.create(**validated_data)
        for subseccion_data in subsecciones_data:
            preguntas_data = subseccion_data.pop("preguntas", [])
            subseccion = SubSeccion.objects.create(seccion=seccion, **subseccion_data)
            for pregunta_data in preguntas_data:
                Pregunta.objects.create(subseccion=subseccion, **pregunta_data)
        return seccion

    def update(self, instance, validated_data):
        subsecciones_data = validated_data.pop("subsecciones", [])
        instance.titulo = validated_data.get("titulo", instance.titulo)
        instance.ponderador = validated_data.get("ponderador", instance.ponderador)
        instance.activo = validated_data.get("activo", instance.activo)
        instance.save()

        # Limpiar subsecciones existentes y recrearlas
        instance.subsecciones.all().delete()
        for subseccion_data in subsecciones_data:
            preguntas_data = subseccion_data.pop("preguntas", [])
            subseccion = SubSeccion.objects.create(seccion=instance, **subseccion_data)
            for pregunta_data in preguntas_data:
                Pregunta.objects.create(subseccion=subseccion, **pregunta_data)
        return instance


class FormularioSerializer(serializers.ModelSerializer):
    secciones = SeccionSerializer(many=True)

    class Meta:
        model = Formulario
        fields = ["id", "titulo", "activo", "secciones"]

    def create(self, validated_data):
        secciones_data = validated_data.pop("secciones", [])
        formulario = Formulario.objects.create(**validated_data)
        for seccion_data in secciones_data:
            subsecciones_data = seccion_data.pop("subsecciones", [])
            seccion = Seccion.objects.create(formulario=formulario, **seccion_data)
            for subseccion_data in subsecciones_data:
                preguntas_data = subseccion_data.pop("preguntas", [])
                subseccion = SubSeccion.objects.create(seccion=seccion, **subseccion_data)
                for pregunta_data in preguntas_data:
                    Pregunta.objects.create(subseccion=subseccion, **pregunta_data)
        return formulario

    def update(self, instance, validated_data):
        secciones_data = validated_data.pop("secciones", [])
        instance.titulo = validated_data.get("titulo", instance.titulo)
        instance.activo = validated_data.get("activo", instance.activo)
        instance.save()

        # Limpiar secciones existentes y recrearlas
        instance.secciones.all().delete()
        for seccion_data in secciones_data:
            subsecciones_data = seccion_data.pop("subsecciones", [])
            seccion = Seccion.objects.create(formulario=instance, **seccion_data)
            for subseccion_data in subsecciones_data:
                preguntas_data = subseccion_data.pop("preguntas", [])
                subseccion = SubSeccion.objects.create(seccion=seccion, **subseccion_data)
                for pregunta_data in preguntas_data:
                    Pregunta.objects.create(subseccion=subseccion, **pregunta_data)
        return instance

#-------------------------------

class RespuestaPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaPregunta
        fields = ["id", "pregunta", "valor", "comentario", "habilitada"]


class RespuestaFormularioSerializer(serializers.ModelSerializer):
    respuestas = RespuestaPreguntaSerializer(many=True)
    calificacion_global = serializers.SerializerMethodField()  # 👈 nuevo campo

    class Meta:
        model = RespuestaFormulario
        fields = ["id", "formulario", "oficina", "descripcion", "fecha", "usuario", "respuestas", "calificacion_global"]

    def create(self, validated_data):
        respuestas_data = validated_data.pop("respuestas", [])
        respuesta_formulario = RespuestaFormulario.objects.create(**validated_data)

        for r in respuestas_data:
            RespuestaPregunta.objects.create(respuesta_formulario=respuesta_formulario, **r)

        return respuesta_formulario

    def get_calificacion_global(self, obj):
        return obj.calcular_calificacion()

    def update(self, instance, validated_data):
        respuestas_data = validated_data.pop("respuestas", [])
        
        # Actualizar campos del formulario
        instance.oficina = validated_data.get("oficina", instance.oficina)
        instance.descripcion = validated_data.get("descripcion", instance.descripcion)
        instance.usuario = validated_data.get("usuario", instance.usuario)
        instance.save()

        # Reemplazar respuestas (Estrategia: Borrar y Recrear)
        instance.respuestas.all().delete()
        for r in respuestas_data:
            RespuestaPregunta.objects.create(respuesta_formulario=instance, **r)

        return instance

class RegistroTemporalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroTemporal
        fields = '__all__'

    def create(self, validated_data):
        last_periodo = Periodo.objects.last()
        if last_periodo:
            validated_data['periodo'] = last_periodo
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Nested serialization for details
        representation['area'] = AreasSerializer(instance.area.all(), many=True).data
        representation['rubro'] = RubrosSerializer(instance.rubro.all(), many=True).data
        
        # Get related action description
        # Using related_name='accionRTemporal' from AccionesTemporal model
        acciones = instance.accionRTemporal.all()
        if acciones.exists():
             accion = acciones.first()
             representation['accion_detalle'] = {
                 'id': accion.idAccion,
                 'descripcion': accion.descripcion,
                 'antecedente': accion.antecedente
             }
             representation['accion_descripcion'] = accion.descripcion # Keep legacy field
        else:
             representation['accion_detalle'] = None
             representation['accion_descripcion'] = "Sin descripción"
             
        return representation

class AccionesTemporalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccionesTemporal
        fields = '__all__'

class AreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
    
class RubrosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = '__all__'

class PeriodosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = '__all__'

class ReporteGeneradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = '__all__'
