from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_dietas, name='lista_dietas'),
    path('crear/', views.crear_dieta, name='crear_dieta'),
    path('dieta/<int:dieta_id>/editar/', views.editar_dieta, name='editar_dieta'),
    path('dieta/<int:dieta_id>/preparar/', views.preparar_dieta_view, name='preparar_dieta'),

    # 🗑️ Papelera
    path('papelera/', views.papelera_dietas, name='papelera_dietas'),
    path('papelera/<int:dieta_id>/restaurar/', views.restaurar_dieta, name='restaurar_dieta'),
    path('dieta/<int:dieta_id>/eliminar/', views.eliminar_dieta, name='eliminar_dieta'),
]