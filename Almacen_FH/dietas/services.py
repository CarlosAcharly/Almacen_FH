from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import Dieta
from movimientos.models import Entrada, Salida


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):

    # Incluimos categoría sin romper nada
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

        # Cantidad válida
        if kg <= 0:
            raise ValidationError(
                f"La cantidad de {producto.nombre} debe ser mayor a 0"
            )

        # Categoría válida
        if producto.categoria.nombre != 'Dietas':
            raise ValidationError(
                f"El producto '{producto.nombre}' no pertenece a la categoría Dietas"
            )

        # Stock suficiente
        if producto.stock_kg < kg:
            raise ValidationError(
                f"Stock insuficiente de {producto.nombre}. "
                f"Disponible: {producto.stock_kg} kg"
            )

    # =========================
    # 2️⃣ DESCONTAR INSUMOS + SALIDA
    # =========================
    for d in detalles:
        producto = d.producto
        kg = Decimal(d.kg)

        producto.stock_kg -= kg
        producto.save(update_fields=['stock_kg'])

        Salida.objects.create(
            producto=producto,
            kg=kg,
            usuario=usuario,
            tipo='DIETA'
        )

    # =========================
    # 3️⃣ AUMENTAR STOCK DE DIETA
    # =========================
    dieta.recalcular_total()

    producto_dieta = dieta.producto_dieta
    producto_dieta.stock_kg += dieta.total_kg
    producto_dieta.save(update_fields=['stock_kg'])

    # =========================
    # 4️⃣ REGISTRAR ENTRADA
    # =========================
    Entrada.objects.create(
        producto=producto_dieta,
        kg=dieta.total_kg,
        usuario=usuario,
        # observaciones=f"Preparación de dieta {dieta.nombre}"
    )
