from django.shortcuts import render
from django.db.models import Sum, F, Q, Count
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required
from datetime import date
from catalogos.models import Producto, Categoria
from movimientos.models import Entrada, Movimiento, MovimientoDetalle
from dietas.models import Dieta, PreparacionDieta

@login_required
def dashboard(request):
    hoy = now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # Filtrar por período
    periodo = request.GET.get('periodo', 'mensual')
    
    if periodo == 'diario':
        fecha_inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'semanal':
        fecha_inicio = inicio_semana
    elif periodo == 'anual':
        fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # mensual (default)
        fecha_inicio = inicio_mes
    
    # ==========================
    # 📦 STOCK GENERAL
    # ==========================
    stock_total = Producto.objects.aggregate(total=Sum('stock_kg'))['total'] or 0
    total_productos = Producto.objects.count()
    productos_con_stock = Producto.objects.filter(stock_kg__gt=0).count()
    
    # ==========================
    # ⚠️ ALERTAS DE STOCK
    # ==========================
    productos_stock_bajo = Producto.objects.filter(
        stock_kg__lte=F('stock_minimo_kg'),
        stock_kg__gt=0
    )[:10]  # Solo primeros 10 para no saturar
    
    productos_criticos = Producto.objects.filter(
        stock_kg=0,
        activo=True
    )[:10]
    
    # ==========================
    # 📊 MOVIMIENTOS (USANDO SISTEMA UNIFICADO)
    # ==========================
    # Entradas del período
    entradas_periodo = Entrada.objects.filter(
        fecha_hora__gte=fecha_inicio
    ).aggregate(total=Sum('kg'))['total'] or 0
    
    # Salidas del período (MovimientoDetalle)
    salidas_periodo = MovimientoDetalle.objects.filter(
        movimiento__fecha_hora__gte=fecha_inicio
    ).aggregate(total=Sum('kg'))['total'] or 0
    
    # Balance
    balance = entradas_periodo - salidas_periodo
    
    # ==========================
    # 🐖 KPIs DE DIETAS
    # ==========================
    # Dietas activas
    dietas_activas = Dieta.objects.filter(activa=True, eliminada=False).count()
    
    # Preparaciones del período
    preparaciones_periodo = PreparacionDieta.objects.filter(
        fecha_hora__gte=fecha_inicio
    ).aggregate(total=Sum('cantidad_preparada'))['total'] or 0
    
    # Últimas preparaciones
    ultimas_preparaciones = PreparacionDieta.objects.select_related(
        'dieta', 'usuario'
    ).order_by('-fecha_hora')[:5]
    
    # ==========================
    # 📈 MOVIMIENTOS POR TIPO
    # ==========================
    movimientos_por_tipo = Movimiento.objects.filter(
        fecha_hora__gte=fecha_inicio
    ).values('tipo').annotate(
        total_kg=Sum('detalles__kg'),
        count=Count('id')
    ).order_by('-total_kg')
    
    # ==========================
    # 🏆 PRODUCTOS MÁS MOVIMIENTOS
    # ==========================
    # Productos con más salidas (ingredientes más usados)
    ingredientes_mas_usados = MovimientoDetalle.objects.filter(
        movimiento__tipo='DIETA',
        movimiento__fecha_hora__gte=fecha_inicio
    ).values(
        'producto__nombre'
    ).annotate(
        total_usado=Sum('kg')
    ).order_by('-total_usado')[:10]
    
    # Productos dietas más producidos
    dietas_mas_producidas = Entrada.objects.filter(
        producto__categoria__nombre='Dietas',
        fecha_hora__gte=fecha_inicio
    ).values(
        'producto__nombre'
    ).annotate(
        total_producido=Sum('kg')
    ).order_by('-total_producido')[:10]
    
    # ==========================
    # 📋 ÚLTIMOS MOVIMIENTOS
    # ==========================
    # Últimos movimientos (combinados)
    ultimos_movimientos = []
    
    # Últimas entradas
    ultimas_entradas = Entrada.objects.select_related(
        'producto', 'usuario', 'proveedor'
    ).order_by('-fecha_hora')[:5]
    
    # Últimos movimientos (ventas, traslados, dietas)
    ultimos_movimientos_general = Movimiento.objects.select_related(
        'usuario', 'cliente'
    ).prefetch_related('detalles__producto').order_by('-fecha_hora')[:5]
    
    # ==========================
    # 📦 CATEGORÍAS CON STOCK
    # ==========================
    categorias_con_stock = Categoria.objects.annotate(
        total_stock=Sum('producto__stock_kg'),
        productos_count=Count('producto')
    ).filter(total_stock__gt=0).order_by('-total_stock')[:5]
    
    # ==========================
    # 🔄 TENDENCIAS
    # ==========================
    # Entradas últimos 7 días
    tendencia_entradas = []
    for i in range(7, -1, -1):
        fecha = hoy - timedelta(days=i)
        fecha_inicio_dia = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin_dia = fecha.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        total_dia = Entrada.objects.filter(
            fecha_hora__range=(fecha_inicio_dia, fecha_fin_dia)
        ).aggregate(total=Sum('kg'))['total'] or 0
        
        tendencia_entradas.append({
            'fecha': fecha.strftime('%d/%m'),
            'total': float(total_dia)
        })
    
    # ==========================
    # CONTEXTO
    # ==========================
    context = {
        'periodo': periodo,
        'fecha_inicio': fecha_inicio.date(),
        
        # KPIs generales
        'stock_total': round(stock_total, 2),
        'total_productos': total_productos,
        'productos_con_stock': productos_con_stock,
        
        # Movimientos
        'entradas_periodo': round(entradas_periodo, 2),
        'salidas_periodo': round(salidas_periodo, 2),
        'balance': round(balance, 2),
        
        # Dietas
        'dietas_activas': dietas_activas,
        'preparaciones_periodo': round(preparaciones_periodo, 2),
        'ultimas_preparaciones': ultimas_preparaciones,
        
        # Alertas
        'productos_stock_bajo': productos_stock_bajo,
        'productos_criticos': productos_criticos,
        'productos_bajos_count': productos_stock_bajo.count(),
        'productos_criticos_count': productos_criticos.count(),
        
        # Estadísticas
        'movimientos_por_tipo': movimientos_por_tipo,
        'ingredientes_mas_usados': ingredientes_mas_usados,
        'dietas_mas_producidas': dietas_mas_producidas,
        'categorias_con_stock': categorias_con_stock,
        
        # Últimos registros
        'ultimas_entradas': ultimas_entradas,
        'ultimos_movimientos': ultimos_movimientos_general,
        
        # Gráficos
        'tendencia_entradas': tendencia_entradas,
        
        # Para compatibilidad con template actual
        'productos': Producto.objects.all()[:20],  # Solo primeros 20 para performance
    }

    return render(request, 'templates/dashboard/index.html', context)