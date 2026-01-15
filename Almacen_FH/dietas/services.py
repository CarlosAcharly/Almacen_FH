from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from movimientos.models import Entrada, Salida
from .models import Dieta


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):

    detalles = dieta.detalles.select_related('producto')

    if not detalles.exists():
        raise ValidationError("La dieta no tiene ingredientes")

    # =========================
    # 1️⃣ VALIDAR STOCK
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
    # 2️⃣ SALIDAS (ingredientes)
    # =========================
    for d in detalles:
        Salida.objects.create(
            producto=d.producto,
            kg=d.kg,
            usuario=usuario,
            tipo='DIETA'
        )

    # =========================
    # 3️⃣ ENTRADA (producto dieta)
    # =========================
    dieta.recalcular_total()

    Entrada.objects.create(
        producto=dieta.producto_dieta,
        kg=dieta.total_kg,
        usuario=usuario,
        fecha_hora=timezone.now()
    )

    # =========================
    # 4️⃣ MARCAR COMO PREPARADA
    # =========================
    dieta.preparada = True
    dieta.fecha_preparacion = timezone.now()
    dieta.save(update_fields=['preparada', 'fecha_preparacion'])
