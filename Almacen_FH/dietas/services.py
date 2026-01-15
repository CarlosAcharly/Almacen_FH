from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from movimientos.models import Entrada, Movimiento, MovimientoDetalle
from catalogos.models import Cliente
from .models import Dieta, PreparacionDieta


@transaction.atomic
def preparar_dieta(dieta: Dieta, usuario, observaciones=''):
    """
    Prepara una dieta usando el sistema unificado de movimientos:
    1. Valida stock de ingredientes
    2. Crea Movimiento tipo 'DIETA'
    3. Crea MovimientoDetalle para cada ingrediente (descuenta stock automáticamente)
    4. Crea Entrada para el producto dieta (aumenta stock)
    5. Registra la preparación en historial
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
    # 2️⃣ CREAR MOVIMIENTO (REGISTRO PRINCIPAL)
    # =========================
    movimiento = Movimiento.objects.create(
        tipo='DIETA',
        usuario=usuario,
        descripcion=f"Preparación: {dieta.nombre} - {observaciones[:50]}" if observaciones else f"Preparación: {dieta.nombre}",
        folio=f"DIETA-{Movimiento.objects.filter(tipo='DIETA').count() + 1:05d}",
        fecha_hora=timezone.now()
    )

    # =========================
    # 3️⃣ CREAR DETALLES DEL MOVIMIENTO (DESCUENTA INGREDIENTES)
    # =========================
    cantidad_preparada = Decimal('0')
    
    for d in detalles:
        producto = d.producto
        kg = Decimal(d.kg)
        
        # ✅ IMPORTANTE: Esto descuenta stock automáticamente en MovimientoDetalle.save()
        MovimientoDetalle.objects.create(
            movimiento=movimiento,
            producto=producto,
            kg=kg,
            toneladas=0,
            bultos=0
        )
        
        cantidad_preparada += kg

    # =========================
    # 4️⃣ ENTRADA (DIETA TERMINADA) - ¡YA ESTABA BIEN!
    # =========================
    producto_dieta = dieta.producto_dieta
    
    # ✅ Esto aumenta stock automáticamente en Entrada.save()
    Entrada.objects.create(
        producto=producto_dieta,
        kg=cantidad_preparada,
        usuario=usuario,
        fecha_hora=timezone.now()
        # proveedor=None se asume automáticamente
    )

    # =========================
    # 5️⃣ REGISTRAR PREPARACIÓN EN HISTORIAL
    # =========================
    PreparacionDieta.objects.create(
        dieta=dieta,
        usuario=usuario,
        cantidad_preparada=cantidad_preparada,
        observaciones=observaciones,
        fecha_hora=timezone.now()
        # Opcional: puedes agregar movimiento=moviemento si quieres enlazarlos
    )

    return cantidad_preparada