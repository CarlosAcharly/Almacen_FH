from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.conf import settings  # Añade esta importación
from catalogos.models import Producto


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
    etapa = models.CharField(
        max_length=20,
        choices=EtapaCerdo.choices
    )

    # Producto terminado que representa la dieta
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

    # Estado
    activa = models.BooleanField(default=True)

    # 🗑️ PAPELERA (soft delete)
    eliminada = models.BooleanField(default=False)
    eliminada_en = models.DateTimeField(null=True, blank=True)

    # ==========================
    # MÉTODOS DE NEGOCIO
    # ==========================

    def recalcular_total(self):
        total = self.detalles.aggregate(
            total=Sum('kg')
        )['total'] or 0

        self.total_kg = total
        self.save(update_fields=['total_kg'])

    def eliminar(self):
        """Enviar dieta a la papelera"""
        self.eliminada = True
        self.activa = False
        self.eliminada_en = timezone.now()
        self.save(update_fields=['eliminada', 'activa', 'eliminada_en'])

    def restaurar(self):
        """Restaurar dieta desde la papelera"""
        self.eliminada = False
        self.activa = True
        self.eliminada_en = None
        self.save(update_fields=['eliminada', 'activa', 'eliminada_en'])

    def __str__(self):
        return f"{self.nombre} ({self.get_etapa_display()})"


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


class PreparacionDieta(models.Model):
    """Registro de cada vez que se prepara una dieta"""
    dieta = models.ForeignKey(
        Dieta,
        on_delete=models.CASCADE,
        related_name='preparaciones'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CORREGIDO: Usar settings.AUTH_USER_MODEL
        on_delete=models.PROTECT
    )
    fecha_hora = models.DateTimeField(default=timezone.now)
    cantidad_preparada = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )
    observaciones = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.dieta.nombre} - {self.cantidad_preparada}kg"