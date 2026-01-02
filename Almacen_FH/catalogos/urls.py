from django.urls import path
from . import views
from .views import lista_proveedores, crear_proveedor, editar_proveedor, eliminar_proveedor

urlpatterns = [
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    
    path('proveedores/', lista_proveedores, name='lista_proveedores'),
    path('proveedores/nuevo/', crear_proveedor, name='crear_proveedor'),
    path('proveedores/editar/<int:pk>/', editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', eliminar_proveedor, name='eliminar_proveedor'),

    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    
    path('choferes/', views.lista_choferes, name='lista_choferes'),
    path('choferes/nuevo/', views.crear_chofer, name='crear_chofer'),
    path('choferes/editar/<int:pk>/', views.editar_chofer, name='editar_chofer'),
    path('choferes/eliminar/<int:pk>/', views.eliminar_chofer, name='eliminar_chofer'),

    path('unidades/', views.lista_unidades, name='lista_unidades'),
    path('unidades/nuevo/', views.crear_unidad, name='crear_unidad'),
    path('unidades/editar/<int:pk>/', views.editar_unidad, name='editar_unidad'),
    path('unidades/eliminar/<int:pk>/', views.eliminar_unidad, name='eliminar_unidad'),

    path('lugares/', views.lista_lugares, name='lista_lugares'),
    path('lugares/nuevo/', views.crear_lugar, name='crear_lugar'),
    path('lugares/editar/<int:pk>/', views.editar_lugar, name='editar_lugar'),
    path('lugares/eliminar/<int:pk>/', views.eliminar_lugar, name='eliminar_lugar'),

    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nuevo/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),


]
