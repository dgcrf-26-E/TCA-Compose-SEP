from django.urls import path
from panel import views

app_name = 'user_admin'

urlpatterns = [
    path('clave/', views.AccessKeyView.as_view(), name='access_key'),
    path('', views.InicioView.as_view(), name='parametros'),

    path('usuarios', views.UsuarioListView.as_view(), name='usuario_list'),
    path('nuevo_user/', views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('<int:pk>/editar_user/', views.UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('<int:pk>/borrar_user/', views.UserDeleteView.as_view(), name='user_delete'),

    path('rubros', views.RubroListView.as_view(), name='rubro_list'),
    path('nuevo_rubro/', views.RubroCreateView.as_view(), name='rubro_create'),
    path('<int:pk>/editar_rubro/', views.RubroUpdateView.as_view(), name='rubro_edit'),
    path('<int:pk>/borrar_rubro/', views.RubroDeleteView.as_view(), name='rubro_delete'),

    path('areas', views.AreaListView.as_view(), name='area_list'),
    path('nuevo_area/', views.AreaCreateView.as_view(), name='area_create'),
    path('<int:pk>/editar_area/', views.AreaUpdateView.as_view(), name='area_edit'),
    path('<int:pk>/borrar_area/', views.AreaDeleteView.as_view(), name='area_delete'),
]