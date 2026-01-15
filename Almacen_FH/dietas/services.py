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
        if d.producto.stock_kg < d.kg:
            raise ValidationError(
                f"Stock insuficiente de {d.producto.nombre}. "
                f"Disponible: {d.producto.stock_kg} kg"
            )

    # =========================
    # 2️⃣ SALIDAS (ingredientes)
    # =========================
    for d in detalles:
        Salida.objects.create(
            producto=d.producto,
            kg=d.kg,
            toneladas=0,
            bultos=0,
            tipo='DIETA',
            usuario=usuario,
            fecha_hora=timezone.now()
        )

    # =========================
    # 3️⃣ ENTRADA (producto dieta)
    # =========================
    dieta.recalcular_total()

    Entrada.objects.create(
        producto=dieta.producto_dieta,
        kg=dieta.total_kg,
        toneladas=0,
        bultos=0,
        usuario=usuario,
        fecha_hora=timezone.now()
    )

    # =========================
    # 4️⃣ MARCAR COMO PREPARADA
    # =========================
    dieta.preparada = True
    dieta.fecha_preparacion = timezone.now()
    dieta.save(update_fields=['preparada', 'fecha_preparacion'])
