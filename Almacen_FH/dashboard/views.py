from django.shortcuts import render
from django.db.models import Sum, F
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from catalogos.models import Producto
from movimientos.models import Entrada, Salida

@login_required
def dashboard(request):
    hoy = now()
    inicio_mes = hoy.replace(day=1)

    # ==========================
    # 📦 STOCK TOTAL
    # ==========================
    stock_total = (
        Producto.objects.aggregate(total=Sum('stock_kg'))['total']
        or 0
    )

    # ==========================
    # ⚠️ STOCK BAJO Y 🔥 CRÍTICO
    # ==========================
    productos_stock_bajo = Producto.objects.filter(
        stock_kg__lte=F('stock_minimo_kg'),
        stock_kg__gt=0
    )

    productos_criticos = Producto.objects.filter(stock_kg=0)

    # ==========================
    # 📥 ENTRADAS DEL MES
    # ==========================
    entradas_mes = (
        Entrada.objects.filter(fecha__gte=inicio_mes)
        .aggregate(total=Sum('cantidad_kg'))['total']
        or 0
    )

    # ==========================
    # 📤 SALIDAS DEL MES
    # ==========================
    salidas_mes = (
        Salida.objects.filter(fecha__gte=inicio_mes)
        .aggregate(total=Sum('cantidad_kg'))['total']
        or 0
    )

    # ==========================
    # ⚖️ BALANCE
    # ==========================
    balance = entradas_mes - salidas_mes

    # ==========================
    # 🕒 ÚLTIMOS MOVIMIENTOS
    # ==========================
    entradas = (
        Entrada.objects
        .select_related('producto', 'usuario')
        .order_by('-fecha_hora')[:5]
    )

    salidas = (
        Salida.objects
        .select_related('producto', 'usuario')
        .order_by('-fecha_hora')[:5]
    )
    movimientos = sorted(
        list(entradas) + list(salidas),
        key=lambda x: x.fecha_hora,
        reverse=True
    )[:10]

    # ==========================
    # 📦 PRODUCTOS
    # ==========================
    productos = Producto.objects.all()

    # ==========================
    # CONTEXT
    # ==========================
    context = {
        # KPIs
        'stock_total': stock_total,
        'entradas_mes': entradas_mes,
        'salidas_mes': salidas_mes,
        'balance': balance,

        # Alertas
        'productos_bajos': productos_stock_bajo.count(),
        'productos_stock_bajo': productos_stock_bajo,
        'productos_criticos': productos_criticos,

        # Datos
        'productos': productos,
        'movimientos': movimientos,
    }

    return render(request, 'dashboard/index.html', context)
