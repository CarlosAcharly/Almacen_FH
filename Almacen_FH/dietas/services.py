from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from movimientos.models import Entrada, Salida
from catalogos.models import Cliente
from .models import Dieta


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):

    detalles = dieta.detalles.select_related('producto')

    if not detalles.exists():
        raise ValidationError("La dieta no tiene ingredientes")

    # =========================
    # CLIENTE INTERNO
    # =========================
    cliente_interno, _ = Cliente.objects.get_or_create(
        nombre='Interno',
        defaults={'activo': True}
    )

    # =========================
    # VALIDAR STOCK
    # =========================
    for d in detalles:
        if d.producto.stock_kg < d.kg:
            raise ValidationError(
                f"Stock insuficiente de {d.producto.nombre}. "
                f"Disponible: {d.producto.stock_kg} kg"
            )

    # =========================
    # SALIDAS (ingredientes)
    # =========================
    for d in detalles:
        Salida.objects.create(
            producto=d.producto,
            kg=d.kg,
            usuario=usuario,
            tipo='VENTA',
            cliente=cliente_interno
        )

    # =========================
    # ENTRADA (producto dieta)
    # =========================
    dieta.recalcular_total()

    Entrada.objects.create(
        producto=dieta.producto_dieta,
        kg=dieta.total_kg,
        usuario=usuario,
        fecha_hora=timezone.now()
    )

    # =========================
    # MARCAR DIETA
    # =========================
    dieta.preparada = True
    dieta.fecha_preparacion = timezone.now()
    dieta.save(update_fields=['preparada', 'fecha_preparacion'])
