from django.urls import path
from . import views
from .views import dashboard
from .views import reporte_mermas_pdf

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('pdf/entradas/', views.pdf_entradas, name='pdf_entradas'),
    path('pdf/salidas/', views.pdf_salidas, name='pdf_salidas'),
    path('pdf/traslado/<int:salida_id>/', views.hoja_traslado, name='hoja_traslado'),
    path('mermas/pdf/<int:anio>/', reporte_mermas_pdf),
    path('mermas/pdf/<int:anio>/<int:mes>/', reporte_mermas_pdf),
    path('mermas/pdf/<int:anio>/', reporte_mermas_pdf, name='pdf_mermas'),
    path('mermas/pdf/<int:anio>/<int:mes>/', reporte_mermas_pdf, name='pdf_mermas'),
]
