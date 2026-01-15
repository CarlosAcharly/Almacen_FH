# reports/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q, FloatField, ExpressionWrapper, Max
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from catalogos.models import Producto, Cliente
from movimientos.models import Entrada, Merma, Movimiento, MovimientoDetalle
from dietas.models import Dieta, PreparacionDieta

@login_required
def dashboard(request):
    # Fechas para filtros
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # Diccionario de meses en español
    MESES_ES = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    # Diccionario de días de la semana
    DIAS_ES = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }
    
    # 1. RESUMEN GENERAL
    total_productos = Producto.objects.filter(eliminado=False).count()
    
    # Productos con stock bajo (menos de 100 kg)
    total_productos_bajo_stock = Producto.objects.filter(
        eliminado=False, 
        stock_kg__lt=100
    ).count()
    
    # 2. MOVIMIENTOS DEL MES
    # Calcular entradas del mes
    try:
        entradas_mes = Entrada.objects.filter(
            fecha_hora__gte=inicio_mes
        ).aggregate(
            total=Sum(F('kg') + F('toneladas') * 1000)
        )['total'] or 0
    except:
        entradas_mes = 0
    
    # Calcular salidas del mes desde MovimientoDetalle
    try:
        salidas_mes = MovimientoDetalle.objects.filter(
            movimiento__fecha_hora__gte=inicio_mes,
            movimiento__tipo__in=['VENTA', 'PEDIDO', 'TRASLADO']
        ).aggregate(total=Sum('kg'))['total'] or 0
    except:
        salidas_mes = 0
    
    # 3. MERMAS DEL MES
    try:
        mermas_mes = Merma.objects.filter(
            fecha_hora__gte=inicio_mes
        ).aggregate(
            total=Sum(F('kg') + F('toneladas') * 1000)
        )['total'] or 0
    except:
        mermas_mes = 0
    
    # 4. DIETAS PREPARADAS RECIENTEMENTE
    try:
        dietas_recientes = PreparacionDieta.objects.select_related(
            'dieta', 'usuario'
        ).order_by('-fecha_hora')[:5]
    except:
        dietas_recientes = []
    
    # 5. ÚLTIMOS MOVIMIENTOS
    try:
        ultimos_movimientos = Movimiento.objects.select_related(
            'cliente', 'lugar', 'usuario'
        ).prefetch_related('detalles').order_by('-fecha_hora')[:10]
    except:
        ultimos_movimientos = []
    
    # 6. PRODUCTOS MÁS VENDIDOS (ÚLTIMOS 30 DÍAS)
    fecha_30_dias = hoy - timedelta(days=30)
    
    try:
        productos_mas_vendidos = Producto.objects.filter(
            movimientodetalle__movimiento__fecha_hora__gte=fecha_30_dias,
            movimientodetalle__movimiento__tipo__in=['VENTA', 'PEDIDO']
        ).annotate(
            total_vendido=Sum('movimientodetalle__kg')
        ).order_by('-total_vendido')[:5]
    except:
        productos_mas_vendidos = []
    
    # 7. ESTADO DE DIETAS
    try:
        dietas_activas = Dieta.objects.filter(eliminada=False).count()
        total_preparaciones = PreparacionDieta.objects.count()
        preparaciones_mes = PreparacionDieta.objects.filter(
            fecha_hora__gte=inicio_mes
        ).count()
    except:
        dietas_activas = 0
        total_preparaciones = 0
        preparaciones_mes = 0
    
    # 8. CLIENTES FRECUENTES (ÚLTIMOS 30 DÍAS)
    clientes_info = []
    try:
        clientes_frecuentes_data = Movimiento.objects.filter(
            fecha_hora__gte=fecha_30_dias,
            cliente__isnull=False
        ).values(
            'cliente__id', 'cliente__nombre'
        ).annotate(
            total_movimientos=Count('id'),
            total_kg=Sum('detalles__kg'),
            ultima_compra=Max('fecha_hora')
        ).order_by('-total_movimientos')[:5]
        
        for item in clientes_frecuentes_data:
            try:
                cliente = Cliente.objects.get(id=item['cliente__id'])
                clientes_info.append({
                    'id': cliente.id,
                    'nombre': cliente.nombre,
                    'telefono': cliente.telefono or 'Sin teléfono',
                    'total_movimientos': item['total_movimientos'] or 0,
                    'total_kg': item['total_kg'] or 0,
                    'ultima_compra': item['ultima_compra']
                })
            except Cliente.DoesNotExist:
                continue
    except Exception as e:
        clientes_info = []
    
    # 9. ALERTAS
    alertas = []
    
    # Productos con stock bajo (menos de 50 kg)
    try:
        productos_bajo_stock = Producto.objects.filter(
            eliminado=False,
            stock_kg__lt=50
        )[:3]
        
        for producto in productos_bajo_stock:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f'{producto.nombre} tiene stock bajo: {producto.stock_kg} kg',
                'icono': '⚠️',
                'link': f'/catalogos/productos/{producto.id}/'
            })
    except:
        pass
    
    # Dietas sin ingredientes
    try:
        dietas_sin_ingredientes = Dieta.objects.filter(
            eliminada=False,
            detalles__isnull=True
        )[:3]
        
        for dieta in dietas_sin_ingredientes:
            alertas.append({
                'tipo': 'info',
                'mensaje': f'Dieta "{dieta.nombre}" no tiene ingredientes',
                'icono': '📝',
                'link': f'/dietas/editar/{dieta.id}/'
            })
    except:
        pass
    
    # Mermas altas recientes (más de 50 kg en la semana)
    try:
        mermas_altas = Merma.objects.filter(
            fecha_hora__gte=inicio_semana,
            kg__gt=50
        ).select_related('producto')[:3]
        
        for merma in mermas_altas:
            alertas.append({
                'tipo': 'danger',
                'mensaje': f'Merma alta: {merma.producto.nombre} - {merma.kg} kg',
                'icono': '🔥',
                'link': '/movimientos/mermas/'
            })
    except:
        pass
    
    # 10. PRODUCTOS CON MÁS ENTRADAS (Este mes)
    try:
        productos_con_mas_entradas = Producto.objects.filter(
            entrada__fecha_hora__gte=inicio_mes
        ).annotate(
            total_entradas=Sum('entrada__kg')
        ).order_by('-total_entradas')[:3]
    except:
        productos_con_mas_entradas = []
    
    # 11. ROTACIÓN DE INVENTARIO
    rotacion_inventario = 0
    try:
        if float(entradas_mes or 0) > 0 and float(salidas_mes or 0) > 0:
            rotacion_inventario = (float(salidas_mes) / float(entradas_mes)) * 100
    except:
        rotacion_inventario = 0
    
    # 12. CALCULAR TOTALES DE ÚLTIMOS MOVIMIENTOS
    total_movimientos_recientes = 0
    for mov in ultimos_movimientos:
        for detalle in mov.detalles.all():
            total_movimientos_recientes += detalle.kg
    
    # Obtener fechas en español
    mes_actual_es = f"{MESES_ES[inicio_mes.month]} {inicio_mes.year}"
    dia_semana_hoy = DIAS_ES.get(hoy.weekday(), '')
    hoy_es = f"{dia_semana_hoy}, {hoy.day} de {MESES_ES[hoy.month]} de {hoy.year}"
    inicio_mes_es = f"{inicio_mes.day} de {MESES_ES[inicio_mes.month]} de {inicio_mes.year}"
    
    context = {
        # Resumen
        'total_productos': total_productos,
        'productos_bajo_stock': total_productos_bajo_stock,
        'entradas_mes': round(float(entradas_mes or 0), 2),
        'salidas_mes': round(float(salidas_mes or 0), 2),
        'mermas_mes': round(float(mermas_mes or 0), 2),
        'dietas_activas': dietas_activas,
        'total_preparaciones': total_preparaciones,
        'preparaciones_mes': preparaciones_mes,
        'rotacion_inventario': round(rotacion_inventario, 2),
        'total_movimientos_recientes': round(total_movimientos_recientes, 2),
        
        # Listas
        'dietas_recientes': dietas_recientes,
        'ultimos_movimientos': ultimos_movimientos,
        'productos_mas_vendidos': productos_mas_vendidos,
        'clientes_frecuentes': clientes_info,
        'productos_con_mas_entradas': productos_con_mas_entradas,
        'alertas': alertas,
        
        # Fechas en español
        'mes_actual': mes_actual_es,
        'hoy_es': hoy_es,
        'inicio_mes_es': inicio_mes_es,
        'mes_actual_nombre': MESES_ES[inicio_mes.month],
        'hoy_dia': hoy.day,
        'hoy_mes': MESES_ES[hoy.month],
        'hoy_ano': hoy.year,
        
        # Diccionarios para uso en template (opcional)
        'meses_es': MESES_ES,
        'dias_es': DIAS_ES,
    }
    
    return render(request, 'reportes/dashboard.html', context)


@login_required
def dashboard_resumen_movimientos(request):
    """Vista para gráficos AJAX de movimientos"""
    hoy = timezone.now()
    
    # Últimos 7 días
    datos_7_dias = []
    for i in range(6, -1, -1):
        fecha = hoy - timedelta(days=i)
        fecha_inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Entradas del día
        try:
            entradas_dia = Entrada.objects.filter(
                fecha_hora__range=(fecha_inicio, fecha_fin)
            ).aggregate(
                total=Sum(F('kg') + F('toneladas') * 1000)
            )['total'] or 0
        except:
            entradas_dia = 0
        
        # Salidas del día
        try:
            salidas_dia = MovimientoDetalle.objects.filter(
                movimiento__fecha_hora__range=(fecha_inicio, fecha_fin),
                movimiento__tipo__in=['VENTA', 'PEDIDO', 'TRASLADO']
            ).aggregate(total=Sum('kg'))['total'] or 0
        except:
            salidas_dia = 0
        
        datos_7_dias.append({
            'fecha': fecha.strftime('%d/%m'),
            'entradas': float(entradas_dia),
            'salidas': float(salidas_dia)
        })
    
    return JsonResponse({'datos_7_dias': datos_7_dias})