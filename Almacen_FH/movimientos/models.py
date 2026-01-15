from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal

from catalogos.models import (
    Producto, Proveedor, Cliente, Lugar,
    Chofer, UnidadTransporte
)


# =========================
# UTILIDAD
# =========================
def calcular_total_kg(producto, kg, toneladas, bultos):
    peso_bulto = getattr(producto, 'peso_por_bulto', None)

    if bultos > 0 and not peso_bulto:
        raise ValidationError(
            f"El producto '{producto}' no tiene peso por bulto definido"
        )

    return (
        Decimal(kg or 0) +
        (Decimal(toneladas or 0) * Decimal(1000)) +
        (Decimal(bultos or 0) * Decimal(peso_bulto or 0))
    )


# =========================
# ENTRADAS
# =========================
class Entrada(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    # 🔥 CLAVE: proveedor opcional (dietas, ajustes internos)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    fecha_hora = models.DateTimeField(auto_now_add=True)

    kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    toneladas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bultos = models.PositiveIntegerField(default=0)

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def clean(self):
        total_kg = calcular_total_kg(
            self.producto, self.kg, self.toneladas, self.bultos
        )

        if total_kg <= 0:
            raise ValidationError("La entrada debe ser mayor a 0 kg")

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        self.clean()

        if es_nuevo:
            total_kg = calcular_total_kg(
                self.producto, self.kg, self.toneladas, self.bultos
            )

            self.producto.stock_kg += total_kg
            self.producto.save()

        super().save(*args, **kwargs)

    def __str__(self):
        origenorei = self.proveedor or "Interno / Dieta"
        return f"Entrada {self.producto} - {origenorei}"


# =========================
# SALIDAS (MODIFICADO: SOLO LECTURA/HISTÓRICO)
# =========================
class Salida(models.Model):
    TIPOS = (
        ('VENTA', 'Venta'),
        ('TRASLADO', 'Traslado'),
        ('PEDIDO', 'Pedido'),
        ('DIETA', 'Dieta'),  # Mantener compatibilidad con datos existentes
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    toneladas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bultos = models.PositiveIntegerField(default=0)

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    lugar = models.ForeignKey(Lugar, on_delete=models.PROTECT, null=True, blank=True)
    chofer = models.ForeignKey(Chofer, on_delete=models.PROTECT, null=True, blank=True)
    unidad = models.ForeignKey(UnidadTransporte, on_delete=models.PROTECT, null=True, blank=True)

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    @property
    def cantidad_total_kg(self):
        return calcular_total_kg(
            self.producto, self.kg, self.toneladas, self.bultos
        )

    def clean(self):
        total_kg = self.cantidad_total_kg

        if total_kg <= 0:
            raise ValidationError("La salida debe ser mayor a 0 kg")

        # 🚨 COMENTADO: Ya no validamos stock aquí porque no restamos
        # if total_kg > self.producto.stock_kg:
        #     raise ValidationError(
        #         f"Stock insuficiente. Disponible: {self.producto.stock_kg} kg"
        #     )

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        self.clean()

        # 🚨 COMENTADO: Ya NO restamos stock aquí
        # Esto evita la duplicación con MovimientoDetalle
        # if es_nuevo:
        #     self.producto.stock_kg -= self.cantidad_total_kg
        #     self.producto.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salida {self.tipo} - {self.producto}"


# =========================
# MERMAS
# =========================
class Merma(models.Model):
    MOTIVOS = (
        ('HUMEDAD', 'Humedad'),
        ('ROTURA', 'Rotura'),
        ('CADUCIDAD', 'Caducidad'),
        ('DERRAME', 'Derrame'),
        ('OTRO', 'Otro'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    motivo = models.CharField(max_length=20, choices=MOTIVOS)
    descripcion = models.TextField(blank=True)

    fecha_hora = models.DateTimeField(auto_now_add=True)

    kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    toneladas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bultos = models.PositiveIntegerField(default=0)

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def clean(self):
        total_kg = calcular_total_kg(
            self.producto, self.kg, self.toneladas, self.bultos
        )

        if total_kg <= 0:
            raise ValidationError("La merma debe ser mayor a 0 kg")

        if total_kg > self.producto.stock_kg:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {self.producto.stock_kg} kg"
            )

    def save(self, *args, **kwargs):
        self.clean()

        total_kg = calcular_total_kg(
            self.producto, self.kg, self.toneladas, self.bultos
        )

        self.producto.stock_kg -= total_kg
        self.producto.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Merma {self.producto} - {self.motivo}"
    

# =========================
# MOVIMIENTO (SISTEMA UNIFICADO)
# =========================
class Movimiento(models.Model):
    TIPOS = (
        ('VENTA', 'Venta'),
        ('TRASLADO', 'Traslado'),
        ('PEDIDO', 'Pedido'),
        ('DIETA', 'Dieta'),  # ✅ AGREGADO: Para preparación de dietas
    )

    folio = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    lugar = models.ForeignKey(Lugar, on_delete=models.PROTECT, null=True, blank=True)
    chofer = models.ForeignKey(Chofer, on_delete=models.PROTECT, null=True, blank=True)
    unidad = models.ForeignKey(UnidadTransporte, on_delete=models.PROTECT, null=True, blank=True)

    # ✅ AGREGADO: Para dietas internas (sin cliente)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-fecha_hora']

    def save(self, *args, **kwargs):
        if not self.folio:
            # Generar folio automático
            ultimo = Movimiento.objects.order_by('-id').first()
            numero = ultimo.id + 1 if ultimo else 1
            self.folio = f"{self.tipo[:3]}-{numero:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - {self.folio}"


class MovimientoDetalle(models.Model):
    movimiento = models.ForeignKey(
        Movimiento,
        related_name='detalles',
        on_delete=models.CASCADE
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    toneladas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bultos = models.PositiveIntegerField(default=0)

    @property
    def total_kg(self):
        return calcular_total_kg(
            self.producto, self.kg, self.toneladas, self.bultos
        )

    def clean(self):
        total = self.total_kg

        if total <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0")

        if total > self.producto.stock_kg:
            raise ValidationError(
                f"Stock insuficiente para {self.producto.nombre}"
            )

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        self.clean()

        if es_nuevo:
            self.producto.stock_kg -= self.total_kg
            self.producto.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto} - {self.total_kg} kg"