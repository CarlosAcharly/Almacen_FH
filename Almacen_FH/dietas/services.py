from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from movimientos.models import Salida, Entrada
from .models import Dieta
from catalogos.models import Cliente, TipoMovimiento


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario):

    detalles = dieta.detalles.select_related('producto')

    if not detalles.exists():
        raise ValidationError("La dieta no tiene ingredientes")

    cliente_interno = Cliente.objects.get(nombre='Interno')
    tipo_venta = TipoMovimiento.objects.get(nombre='Venta')

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
    # 2️⃣ CREAR SALIDAS (INGREDIENTES)
    # =========================
    for d in detalles:
        Salida.objects.create(
            producto=d.producto,
            kg=d.kg,
            toneladas=0,
            bultos=0,
            tipo=tipo_venta,
            cliente=cliente_interno,
            usuario=usuario,
            fecha_hora=timezone.now()
        )

    # =========================
    # 3️⃣ ENTRADA (DIETA PREPARADA)
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
    # 4️⃣ MARCAR DIETA
    # =========================
    dieta.preparada = True
    dieta.fecha_preparacion = timezone.now()
    dieta.save(update_fields=['preparada', 'fecha_preparacion'])
