# dietas/urls.py
from django.urls import path
from . import views
from .views import preparar_dieta_view, editar_dieta, lista_dietas

urlpatterns = [
    path('', views.lista_dietas, name='lista_dietas'),
    path('crear/', views.crear_dieta, name='crear_dieta'),
    path('dieta/<int:dieta_id>/editar/', views.editar_dieta, name='editar_dieta'),
    path('dieta/<int:dieta_id>/preparar/', views.preparar_dieta_view, name='preparar_dieta'),
    ]
