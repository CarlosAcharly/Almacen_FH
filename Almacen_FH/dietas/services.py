from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from movimientos.models import Entrada, Salida
from catalogos.models import Cliente
from .models import Dieta, PreparacionDieta


def asegurar_cliente_interno():
    """Asegura que exista el cliente 'Interno' para salidas de dieta"""
    cliente, created = Cliente.objects.get_or_create(
        nombre='Interno',
        defaults={'telefono': 'N/A'}
    )
    return cliente


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario, observaciones=''):
    """
    Prepara una dieta (puede ejecutarse múltiples veces):
    - Descuenta ingredientes (SALIDA con tipo 'VENTA' y cliente 'Interno')
    - Aumenta stock del producto dieta (ENTRADA)
    - Registra la preparación en historial
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
    # 2️⃣ PREPARAR CLIENTE INTERNO
    # =========================
    cliente_interno = asegurar_cliente_interno()

    # =========================
    # 3️⃣ SALIDAS (INGREDIENTES) - Tipo: Venta, Cliente: Interno
    # =========================
    for d in detalles:
        producto = d.producto
        kg = Decimal(d.kg)

        # Descontar stock
        producto.stock_kg -= kg
        producto.save(update_fields=['stock_kg'])

        # Registrar salida tipo VENTA para cada ingrediente
        Salida.objects.create(
            producto=producto,
            kg=kg,
            usuario=usuario,
            tipo='VENTA',
            fecha_hora=timezone.now(),
            observaciones=f"Preparación de dieta: {dieta.nombre}"
        )

    # =========================
    # 4️⃣ ENTRADA (DIETA TERMINADA)
    # =========================
    cantidad_preparada = dieta.total_kg

    producto_dieta = dieta.producto_dieta
    producto_dieta.stock_kg += cantidad_preparada
    producto_dieta.save(update_fields=['stock_kg'])

    # Registrar entrada automática del producto dieta
    Entrada.objects.create(
        producto=producto_dieta,
        kg=cantidad_preparada,
        usuario=usuario,
        fecha_hora=timezone.now(),
        observaciones=f"Preparación de dieta: {dieta.nombre}"
    )

    # =========================
    # 5️⃣ REGISTRAR PREPARACIÓN EN HISTORIAL
    # =========================
    PreparacionDieta.objects.create(
        dieta=dieta,
        usuario=usuario,
        cantidad_preparada=cantidad_preparada,
        observaciones=observaciones
    )

    return cantidad_preparada