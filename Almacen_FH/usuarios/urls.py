# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Rutas para administradores (sin 'usuarios/' al inicio)
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('credenciales/', views.credenciales_usuario, name='credenciales_usuario'),
    path('<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('<int:usuario_id>/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('mostrar-contrasena/', views.mostrar_contrasena, name='mostrar_contrasena'),
    path('<int:usuario_id>/cambiar-estado/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),
    path('<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # Rutas para perfil (estas van directo)
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/cambiar-contrasena/', views.cambiar_mi_contrasena, name='cambiar_mi_contrasena'),
]