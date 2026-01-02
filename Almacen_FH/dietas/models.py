from django.db import models
from django.conf import settings
from catalogos.models import Producto


# =========================
# ETAPAS DE DIETA (CERDO)
# =========================
class EtapaDieta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


# =========================
# DIETA (MEZCLADO)
# =========================
class Dieta(models.Model):
    etapa = models.ForeignKey(EtapaDieta, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    total_kg = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"Dieta {self.etapa} - {self.fecha_hora.strftime('%d/%m/%Y')}"


# =========================
# DETALLE DE INSUMOS
# =========================
class DietaDetalle(models.Model):
    dieta = models.ForeignKey(
        Dieta,
        related_name='detalles',
        on_delete=models.CASCADE
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    kg = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"{self.producto} - {self.kg} kg"
