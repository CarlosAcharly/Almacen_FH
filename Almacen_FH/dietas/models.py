from django.db import models
from catalogos.models import Producto
from django.db.models import Sum


class EtapaCerdo(models.TextChoices):
    PRE_INICIO = 'pre_inicio', 'Pre-inicio'
    INICIADOR = 'iniciador', 'Iniciador'
    CRECIMIENTO = 'crecimiento', 'Crecimiento'
    DESARROLLO = 'desarrollo', 'Desarrollo'
    ENGORDA = 'engorda', 'Engorda'
    GESTACION = 'gestacion', 'Gestación'
    LACTACION = 'lactacion', 'Lactación'


class Dieta(models.Model):
    nombre = models.CharField(max_length=150)
    etapa = models.CharField(max_length=20, choices=EtapaCerdo.choices)

    producto_dieta = models.OneToOneField(
        Producto,
        on_delete=models.PROTECT,
        related_name='dieta'
    )

    total_kg = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def recalcular_total(self):
        total = self.detalles.aggregate(
            total=Sum('kg')
        )['total'] or 0

        self.total_kg = total
        self.save(update_fields=['total_kg'])

class DetalleDieta(models.Model):
    dieta = models.ForeignKey(
        Dieta,
        related_name='detalles',
        on_delete=models.CASCADE
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )

    kg = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        unique_together = ('dieta', 'producto')

    def __str__(self):
        return f"{self.producto.nombre} - {self.kg} kg"
