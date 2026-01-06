from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db import transaction
from catalogos.models import Producto
from .forms import (
    MovimientoForm, MovimientoDetalleFormSet,
    EntradaForm, SalidaForm, MermaForm
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
# SALIDAS
# =========================
@login_required
def lista_salidas(request):
    salidas = Movimiento.objects.select_related(
        'cliente', 'lugar', 'chofer', 'unidad', 'usuario'
    ).prefetch_related('detalles__producto').order_by('-fecha_hora')
    return render(request, 'movimientos/salidas/lista.html', {'salidas': salidas})





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
# KARDEX POR PRODUCTO
# =========================
@login_required
def kardex_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    peso_bulto = producto.peso_por_bulto or 0

    entradas = Entrada.objects.filter(producto=producto)
    salidas = Salida.objects.filter(producto=producto)
    mermas = Merma.objects.filter(producto=producto)

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

    # SALIDAS
    for s in salidas:
        movimientos.append({
            'fecha': s.fecha_hora,
            'tipo': f'SALIDA ({s.tipo})',
            'cantidad': -total_kg(s),
            'usuario': s.usuario
        })

    # MERMAS
    for m in mermas:
        movimientos.append({
            'fecha': m.fecha_hora,
            'tipo': 'MERMA',
            'cantidad': -total_kg(m),
            'usuario': m.usuario
        })

    # Orden cronológico
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
# CREAR SALIDA (CON FORMSET DINÁMICO)
# =========================


@login_required
def crear_salida(request):
    prefix = 'detalles'  # Debe coincidir con el prefijo del formset

    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        formset = MovimientoDetalleFormSet(request.POST, prefix=prefix)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                movimiento = form.save(commit=False)
                movimiento.usuario = request.user
                movimiento.folio = f"SAL-{Movimiento.objects.count() + 1:05d}"
                movimiento.save()

                detalles = formset.save(commit=False)
                for detalle in detalles:
                    detalle.movimiento = movimiento
                    detalle.save()

            return redirect('lista_salidas')
    else:
        form = MovimientoForm()
        formset = MovimientoDetalleFormSet(queryset=MovimientoDetalle.objects.none(), prefix=prefix)

    productos = Producto.objects.filter(activo=True)

    return render(request, 'movimientos/salidas/crear.html', {
        'form': form,
        'formset': formset,
        'productos': productos,
        'prefix': prefix
    })