from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from movimientos.models import Entrada, Salida
from .models import Dieta


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):
    """
    Prepara una dieta:
    - Descuenta ingredientes (SALIDA)
    - Aumenta stock del producto dieta (ENTRADA)
    - Puede ejecutarse múltiples veces
    """

    detalles = dieta.detalles.select_related(
        'producto',
        'producto__categoria'
    )

    if not detalles.exists():
        raise ValidationError("La dieta no tiene ingredientes")

    # =========================
    # 1️⃣ VALIDACIONES
    # =========================
    for d in detalles:
        producto = d.producto
        kg = Decimal(d.kg)

        if kg <= 0:
            raise ValidationError(
                f"La cantidad de {producto.nombre} debe ser mayor a 0"
            )

        if producto.categoria.nombre != 'Ingrediente de dieta':
            raise ValidationError(
                f"{producto.nombre} no es un ingrediente de dieta"
            )

        if producto.stock_kg < kg:
            raise ValidationError(
                f"Stock insuficiente de {producto.nombre}. "
                f"Disponible: {producto.stock_kg} kg"
            )

    # =========================
    # 2️⃣ SALIDAS (INGREDIENTES)
    # =========================
    for d in detalles:
        producto = d.producto
        kg = Decimal(d.kg)

        # Descontar stock
        producto.stock_kg -= kg
        producto.save(update_fields=['stock_kg'])

        # Registrar salida
        Salida.objects.create(
            producto=producto,
            kg=kg,
            usuario=usuario,
            tipo='DIETA',
            fecha_hora=timezone.now()
        )

    # =========================
    # 3️⃣ ENTRADA (DIETA TERMINADA)
    # =========================
    dieta.recalcular_total()

    producto_dieta = dieta.producto_dieta
    producto_dieta.stock_kg += dieta.total_kg
    producto_dieta.save(update_fields=['stock_kg'])

    Entrada.objects.create(
        producto=producto_dieta,
        kg=dieta.total_kg,
        usuario=usuario,
        fecha_hora=timezone.now()
    )
