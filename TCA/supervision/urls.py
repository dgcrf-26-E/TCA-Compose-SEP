from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccessKeyView,
    InicioView,

    FormularioViewSet,
    SeccionViewSet,
    SubSeccionViewSet,
    PreguntaViewSet,
    RespuestaFormularioViewSet,
    RegistroTemporalViewSet,
    AccionesTemporalViewSet,

    AreasViewSet,
    RubrosViewSet,
    PeriodosViewSet,
    ReporteGeneradoViewSet,

    generar_word,
    guardar_exportar,
)

app_name = 'superv_urls'

router = DefaultRouter()
router.register(r'formularios', FormularioViewSet, basename='formularios')
router.register(r'secciones', SeccionViewSet, basename='secciones')
router.register(r'subsecciones', SubSeccionViewSet, basename='subsecciones')
router.register(r'preguntas', PreguntaViewSet, basename='preguntas')
router.register(r'respuestas', RespuestaFormularioViewSet, basename='respuestas')
router.register(r'registro_temporal', RegistroTemporalViewSet, basename='registro_temporal')
router.register(r'acciones_temporal', AccionesTemporalViewSet, basename='acciones_temporal')
router.register(r'areas', AreasViewSet, basename='areas')
router.register(r'rubros', RubrosViewSet, basename='rubros')
router.register(r'periodos', PeriodosViewSet, basename='periodos')
router.register(r'reporte_final', ReporteGeneradoViewSet, basename='reporte_final')

urlpatterns = [
    path('clave/', AccessKeyView.as_view(), name='access_key'),
    path('', InicioView.as_view(), name='index'),
    path('registro/', InicioView.as_view(), name='registro'),
    path('instrucciones/', InicioView.as_view(), name='instrucciones'),
    path('reportes/', InicioView.as_view(), name='reportes'),
    path('api/', include(router.urls)),
    path('descargar-reporte/', generar_word, name='descargar_reporte'),
    path('guardar-reporte/', guardar_exportar, name='guardar_reporte'),
]
