"""
URL configuration for tablero_control project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as viewsL
from . import views
from django.urls import path, include
from usuarios.views import index, pagina404
import dashboard.views as vDash
 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('administrar/', include('panel.urls')),
    # path('supervision/', include('supervision.urls')),
    
    path('', index, name="index"),
    path('log-in/', viewsL.LoginView.as_view(template_name= 'base/log_in.html'), name='log-in'),
    path('log-out/', viewsL.LogoutView.as_view(), name="logout"),
    path('dashboard/', vDash.dashboard ,name="dashboard" ),
    path('notificacion_leida/<int:notificacion_id>/', vDash.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    
    path('crear_registro/', vDash.crear_registro ,name="crear_registro" ),
    path('crear_registroN/', vDash.AcuerdoCreateNew.as_view() ,name="crear_registroN" ),

    path('detalles/<int:registro_id>/', vDash.detalles , name='detalles'),
    path('carga_masiva/', vDash.cargaMasiva , name='carga_masiva'),

    path('editar_registro/<int:id>/', vDash.editar_registro, name='editar_registro'),

    path('eliminar/<int:idRegistro>/', vDash.eliminar_registro, name='eliminar_registro'),

    path('eliminarM/<int:idMensaje>/', vDash.eliminar_mensaje, name='eliminar_mensaje'),

    path("listas", vDash.paginarRegistros, name="article-list"),

    path('estadistica/', include('estadistica.urls')),

    path('descargas/<int:registro_id>/', vDash.descargar_archivos_acuerdo, name='archivos_acuerdo')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = pagina404