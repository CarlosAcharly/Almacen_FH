from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from movimientos.models import Entrada, Salida
from catalogos.models import Cliente
from .models import Dieta


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):

    if dieta.preparada:
        raise ValidationError("Esta dieta ya fue preparada")

    detalles = dieta.detalles.select_related('producto')

    if not detalles.exists():
        raise ValidationError("La dieta no tiene ingredientes")

    # =========================
    # VALIDACIONES (solo leer stock)
    # =========================
    for d in detalles:
        kg = Decimal(d.kg)
        producto = d.producto

        if producto.stock_kg < kg:
            raise ValidationError(
                f"Stock insuficiente de {producto.nombre}. "
                f"Disponible: {producto.stock_kg} kg"
            )

    # =========================
    # SALIDAS (NO tocar stock aquí)
    # =========================
    cliente_interno = Cliente.objects.get(nombre__iexact='Interno')

    for d in detalles:
        Salida.objects.create(
            producto=d.producto,
            kg=d.kg,
            usuario=usuario,
            tipo='VENTA',
            cliente=cliente_interno
        )
        # ⛔ NO modificar stock manualmente

    # =========================
    # ENTRADA DE LA DIETA
    # =========================
    dieta.recalcular_total()

    Entrada.objects.create(
        producto=dieta.producto_dieta,
        kg=dieta.total_kg,
        usuario=usuario
        # proveedor NULL = interno/dieta (correcto)
    )

    # =========================
    # MARCAR COMO PREPARADA
    # =========================
    dieta.preparada = True
    dieta.fecha_preparacion = timezone.now()
    dieta.save(update_fields=['preparada', 'fecha_preparacion'])
