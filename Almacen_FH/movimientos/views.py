from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db import transaction
from catalogos.models import Producto
from .forms import (
    MovimientoForm, MovimientoDetalleFormSet,
    EntradaForm, SalidaForm, MermaForm, DietaForm
)
from .models import Entrada, Salida, Merma, Movimiento, MovimientoDetalle

# =========================
# ENTRADAS
# =========================
@login_required
def lista_entradas(request):
    entradas = Entrada.objects.select_related(
        'producto', 'proveedor', 'usuario'
    ).order_by('-fecha_hora')

    return render(request, 'movimientos/entradas/lista.html', {
        'entradas': entradas
    })


@login_required
def nueva_entrada(request):
    form = EntradaForm(request.POST or None)
    productos = Producto.objects.all()

    if form.is_valid():
        entrada = form.save(commit=False)
        entrada.usuario = request.user
        entrada.save()
        return redirect('lista_entradas')

    return render(request, 'movimientos/entradas/crear.html', {
        'form': form,
        'productos': productos
    })


# =========================
# SALIDAS (USANDO MOVIMIENTO)
# =========================
@login_required
def lista_salidas(request):
    # Mostrar TODOS los movimientos (ventas, traslados, pedidos, dietas)
    movimientos = Movimiento.objects.select_related(
        'cliente', 'lugar', 'chofer', 'unidad', 'usuario'
    ).prefetch_related('detalles__producto').order_by('-fecha_hora')
    
    # Filtrar por tipo si se solicita
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        movimientos = movimientos.filter(tipo=tipo_filtro)
    
    return render(request, 'movimientos/salidas/lista.html', {
        'movimientos': movimientos,
        'tipo_filtro': tipo_filtro
    })


@login_required
def crear_salida(request):
    prefix = 'detalles'
    ticket_id = None

    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        formset = MovimientoDetalleFormSet(request.POST, prefix=prefix)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                movimiento = form.save(commit=False)
                movimiento.usuario = request.user
                movimiento.save()  # El folio se genera automáticamente en el modelo

                detalles = formset.save(commit=False)
                for detalle in detalles:
                    detalle.movimiento = movimiento
                    detalle.save()

            ticket_id = movimiento.id
            form = MovimientoForm()
            formset = MovimientoDetalleFormSet(queryset=MovimientoDetalle.objects.none(), prefix=prefix)

    else:
        form = MovimientoForm()
        formset = MovimientoDetalleFormSet(queryset=MovimientoDetalle.objects.none(), prefix=prefix)

    productos = Producto.objects.filter(activo=True)

    return render(request, 'movimientos/salidas/crear.html', {
        'form': form,
        'formset': formset,
        'productos': productos,
        'prefix': prefix,
        'ticket_id': ticket_id,
    })


# =========================
# DIETAS (USANDO MOVIMIENTO TIPO='DIETA')
# =========================
@login_required
def lista_dietas(request):
    dietas = Movimiento.objects.filter(tipo='DIETA').select_related(
        'usuario'
    ).prefetch_related('detalles__producto').order_by('-fecha_hora')
    
    return render(request, 'templates/dietas/lista.html', {
        'dietas': dietas
    })


@login_required
def preparar_dieta(request):
    prefix = 'detalles'
    ticket_id = None

    if request.method == 'POST':
        # Forzar tipo DIETA
        post_data = request.POST.copy()
        post_data['tipo'] = 'DIETA'
        
        form = MovimientoForm(post_data)
        formset = MovimientoDetalleFormSet(post_data, prefix=prefix)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                movimiento = form.save(commit=False)
                movimiento.tipo = 'DIETA'  # Asegurar tipo DIETA
                movimiento.usuario = request.user
                movimiento.save()

                detalles = formset.save(commit=False)
                for detalle in detalles:
                    detalle.movimiento = movimiento
                    detalle.save()

            ticket_id = movimiento.id
            form = MovimientoForm(initial={'tipo': 'DIETA'})
            formset = MovimientoDetalleFormSet(queryset=MovimientoDetalle.objects.none(), prefix=prefix)

    else:
        form = MovimientoForm(initial={'tipo': 'DIETA'})
        formset = MovimientoDetalleFormSet(queryset=MovimientoDetalle.objects.none(), prefix=prefix)

    productos = Producto.objects.filter(activo=True)

    return render(request, 'templates/dietas/crear_dieta.html', {
        'form': form,
        'formset': formset,
        'productos': productos,
        'prefix': prefix,
        'ticket_id': ticket_id,
    })


# =========================
# IMPRESIÓN DE TICKET
# =========================
@login_required
def imprimir_ticket(request, movimiento_id):
    movimiento = get_object_or_404(Movimiento, id=movimiento_id)
    detalles = movimiento.detalles.select_related('producto').all()

    total_kg = 0
    total_ton = 0

    for d in detalles:
        total_kg += d.kg
        total_ton += d.toneladas

    return render(request, 'movimientos/salidas/ticket.html', {
        'movimiento': movimiento,
        'detalles': detalles,
        'total_kg': round(total_kg, 2),
        'total_ton': round(total_ton, 3),
    })


# =========================
# MERMAS
# =========================
@login_required
def lista_mermas(request):
    mermas = Merma.objects.select_related('producto').order_by('-fecha_hora')

    anio = request.GET.get('anio')
    mes = request.GET.get('mes')

    if anio:
        mermas = mermas.filter(fecha_hora__year=anio)
    if mes:
        mermas = mermas.filter(fecha_hora__month=mes)

    current_year = date.today().year

    return render(request, 'movimientos/mermas/lista.html', {
        'mermas': mermas,
        'current_year': current_year
    })


@login_required
def crear_merma(request):
    form = MermaForm(request.POST or None)
    if form.is_valid():
        merma = form.save(commit=False)
        merma.usuario = request.user
        merma.save()
        return redirect('lista_mermas')

    return render(request, 'movimientos/mermas/crear.html', {
        'form': form
    })


# =========================
# KARDEX POR PRODUCTO (ACTUALIZADO)
# =========================
@login_required
def kardex_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    peso_bulto = producto.peso_por_bulto or 0

    entradas = Entrada.objects.filter(producto=producto)
    mermas = Merma.objects.filter(producto=producto)
    
    # Obtener movimientos (incluyendo dietas) desde MovimientoDetalle
    movimientos_detalle = MovimientoDetalle.objects.filter(
        producto=producto
    ).select_related('movimiento', 'movimiento__usuario')

    movimientos = []

    def total_kg(obj):
        return (
            obj.kg +
            (obj.toneladas * 1000) +
            (obj.bultos * peso_bulto)
        )

    # ENTRADAS
    for e in entradas:
        movimientos.append({
            'fecha': e.fecha_hora,
            'tipo': 'ENTRADA',
            'cantidad': total_kg(e),
            'usuario': e.usuario
        })

    # MOVIMIENTOS (SALIDAS, DIETAS, etc.)
    for md in movimientos_detalle:
        movimientos.append({
            'fecha': md.movimiento.fecha_hora,
            'tipo': f'{md.movimiento.tipo}',
            'cantidad': -md.total_kg,
            'usuario': md.movimiento.usuario,
            'folio': md.movimiento.folio
        })

    # MERMAS
    for m in mermas:
        movimientos.append({
            'fecha': m.fecha_hora,
            'tipo': 'MERMA',
            'cantidad': -total_kg(m),
            'usuario': m.usuario
        })

    movimientos.sort(key=lambda x: x['fecha'])

    # Stock acumulado
    stock = 0
    for mov in movimientos:
        stock += mov['cantidad']
        mov['stock'] = round(stock, 2)

    return render(request, 'movimientos/kardex.html', {
        'producto': producto,
        'movimientos': movimientos
    })


# =========================
# DETALLE DE MOVIMIENTO
# =========================
@login_required
def detalle_movimiento(request, movimiento_id):
    movimiento = get_object_or_404(Movimiento, id=movimiento_id)
    detalles = movimiento.detalles.select_related('producto').all()
    
    total_kg = sum(d.kg for d in detalles)
    total_ton = sum(d.toneladas for d in detalles)
    
    return render(request, 'movimientos/detalle.html', {
        'movimiento': movimiento,
        'detalles': detalles,
        'total_kg': total_kg,
        'total_ton': total_ton
    })