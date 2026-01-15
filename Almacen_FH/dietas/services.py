from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from .models import Dieta
from movimientos.models import Entrada, Salida


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):

    detalles = dieta.detalles.select_related(
        'producto',
        'producto__categoria'
    )

    # =========================
    # 0️⃣ VALIDACIONES BÁSICAS
    # =========================
    if dieta.preparada:
        raise ValidationError("Esta dieta ya fue preparada")

    if not detalles.exists():
        raise ValidationError("La dieta no tiene ingredientes")

    # =========================
    # 1️⃣ VALIDAR INGREDIENTES
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
                f"El producto '{producto.nombre}' no es un ingrediente de dieta"
            )

        if producto.stock_kg < kg:
            raise ValidationError(
                f"Stock insuficiente de {producto.nombre}. "
                f"Disponible: {producto.stock_kg} kg"
            )

    # =========================
    # 2️⃣ DESCONTAR INGREDIENTES
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
    # 3️⃣ AUMENTAR STOCK DIETA
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
    )

    # =========================
    # 5️⃣ MARCAR DIETA PREPARADA
    # =========================
    dieta.preparada = True
    dieta.fecha_preparacion = timezone.now()
    dieta.save(update_fields=['preparada', 'fecha_preparacion'])
