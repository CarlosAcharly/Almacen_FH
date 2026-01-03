from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Dieta
from movimientos.models import Entrada, Salida


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):

    detalles = dieta.detalles.select_related('producto')

    if not detalles.exists():
        raise ValidationError("La dieta no tiene ingredientes")

    # 1️⃣ Validar stock
    for d in detalles:
        if d.producto.stock_kg < d.kg:
            raise ValidationError(
                f"Stock insuficiente de {d.producto.nombre}"
            )

    # 2️⃣ Descontar insumos + registrar salida
    for d in detalles:
        producto = d.producto
        producto.stock_kg -= d.kg
        producto.save(update_fields=['stock_kg'])

        Salida.objects.create(
            producto=producto,
            kg=d.kg,
            usuario=usuario,
            tipo='DIETA'
        )

    # 3️⃣ Aumentar stock dieta
    dieta.recalcular_total()
    producto_dieta = dieta.producto_dieta
    producto_dieta.stock_kg += dieta.total_kg
    producto_dieta.save(update_fields=['stock_kg'])

    # 4️⃣ Registrar entrada
    Entrada.objects.create(
        producto=producto_dieta,
        kg=dieta.total_kg,
        usuario=usuario,
        #observaciones=f"Preparación de dieta {dieta.nombre}"
    )
