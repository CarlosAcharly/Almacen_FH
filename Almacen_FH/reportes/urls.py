# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/resumen-movimientos/', views.dashboard_resumen_movimientos, name='dashboard_resumen_movimientos'),
    # ... otras URLs que ya tengas
]