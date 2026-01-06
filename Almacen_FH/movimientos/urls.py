from django.urls import path
from . import views

urlpatterns = [
    # ENTRADAS
    path('entradas/', views.lista_entradas, name='lista_entradas'),
    path('entradas/nueva/', views.nueva_entrada, name='nueva_entrada'),

    # SALIDAS
    path('salidas/', views.lista_salidas, name='lista_salidas'),
    path('salidas/nueva/', views.crear_salida, name='crear_salida'),
    # MERMAS
    path('mermas/', views.lista_mermas, name='lista_mermas'),
    path('mermas/nueva/', views.crear_merma, name='crear_merma'),

    # KARDEX
    path('kardex/<int:producto_id>/', views.kardex_producto, name='kardex_producto'),

]
