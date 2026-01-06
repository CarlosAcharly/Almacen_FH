from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from decimal import Decimal

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from weasyprint import HTML

from catalogos.models import Producto
from movimientos.models import Entrada, Salida, Merma
from .utils import encabezado_pdf


# ==========================
# UTILIDAD GENERAL
# ==========================
def total_kg_movimiento(mov):
    """
    Convierte cualquier movimiento a KG evitando NoneType
    """
    kg = mov.kg or Decimal('0')
    toneladas = mov.toneladas or Decimal('0')
    bultos = mov.bultos or Decimal('0')
    peso_bulto = mov.producto.peso_por_bulto or Decimal('0')

    return (
        kg +
        (toneladas * Decimal('1000')) +
        (bultos * peso_bulto)
    )


# ==========================
# DASHBOARD
# ==========================
@login_required
def dashboard(request):
    hoy = date.today()
    periodo = request.GET.get('periodo', 'mensual')

    if periodo == 'diario':
        inicio = hoy
    elif periodo == 'semanal':
        inicio = hoy - timedelta(days=7)
    elif periodo == 'anual':
        inicio = hoy.replace(month=1, day=1)
    else:  # mensual
        inicio = hoy.replace(day=1)

    entradas = Entrada.objects.filter(
        fecha_hora__date__gte=inicio
    ).select_related('producto')

    salidas = Salida.objects.filter(
        fecha_hora__date__gte=inicio
    ).select_related('producto')

    total_entradas = sum(
        total_kg_movimiento(e) for e in entradas
    )

    total_salidas = sum(
        total_kg_movimiento(s) for s in salidas
    )

    productos = Producto.objects.all()

    context = {
        'periodo': periodo,
        'total_entradas': total_entradas,
        'total_salidas': total_salidas,
        'productos': productos
    }

    return render(request, 'reportes/dashboard.html', context)


# ==========================
# PDF ENTRADAS
# ==========================
def pdf_entradas(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_entradas.pdf"'

    p = canvas.Canvas(response, pagesize=LETTER)
    encabezado_pdf(p, "Reporte de Entradas")

    y = 650
    p.setFont("Helvetica", 10)

    entradas = Entrada.objects.select_related('producto').order_by('-fecha_hora')

    for e in entradas:
        total = total_kg_movimiento(e)

        p.drawString(
            40, y,
            f"{e.fecha_hora.strftime('%d/%m/%Y')} - {e.producto.nombre}"
        )
        p.drawString(320, y, f"{total} kg")

        y -= 20

        if y < 50:
            p.showPage()
            encabezado_pdf(p, "Reporte de Entradas")
            p.setFont("Helvetica", 10)
            y = 650

    p.showPage()
    p.save()
    return response


# ==========================
# PDF SALIDAS
# ==========================
def pdf_salidas(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_salidas.pdf"'

    p = canvas.Canvas(response, pagesize=LETTER)
    encabezado_pdf(p, "Reporte de Salidas")

    y = 650
    p.setFont("Helvetica", 10)

    salidas = Salida.objects.select_related('producto').order_by('-fecha_hora')

    for s in salidas:
        total = total_kg_movimiento(s)

        p.drawString(
            40, y,
            f"{s.fecha_hora.strftime('%d/%m/%Y')} - {s.producto.nombre}"
        )
        p.drawString(240, y, f"{s.tipo}")
        p.drawString(340, y, f"{total} kg")

        y -= 20

        if y < 50:
            p.showPage()
            encabezado_pdf(p, "Reporte de Salidas")
            p.setFont("Helvetica", 10)
            y = 650

    p.showPage()
    p.save()
    return response


# ==========================
# HOJA DE TRASLADO
# ==========================
def hoja_traslado(request, salida_id):
    salida = Salida.objects.select_related('producto').get(id=salida_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="hoja_traslado.pdf"'

    p = canvas.Canvas(response, pagesize=LETTER)
    encabezado_pdf(p, "Hoja de Traslado")

    p.setFont("Helvetica", 11)
    y = 650

    total = total_kg_movimiento(salida)

    p.drawString(40, y, f"Fecha: {salida.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
    y -= 30

    p.drawString(40, y, f"Producto: {salida.producto.nombre}")
    y -= 20

    p.drawString(40, y, f"Cantidad total (kg): {total}")
    y -= 20

    p.drawString(40, y, f"Chofer: {salida.chofer}")
    y -= 20

    p.drawString(40, y, f"Unidad: {salida.unidad}")
    y -= 40

    p.drawString(40, y, "Firma Chofer: ____________________________")
    y -= 40

    p.drawString(40, y, "Observaciones:")

    p.showPage()
    p.save()
    return response


# ==========================
# REPORTE DE MERMAS (WEASYPRINT)
# ==========================
def reporte_mermas_pdf(request, anio, mes=None):
    if mes:
        mermas = Merma.objects.filter(
            fecha_hora__year=anio,
            fecha_hora__month=mes
        )
        titulo = f"Reporte de Mermas - {mes}/{anio}"
        nombre = f"mermas_{mes}_{anio}.pdf"
    else:
        mermas = Merma.objects.filter(
            fecha_hora__year=anio
        )
        titulo = f"Reporte Anual de Mermas - {anio}"
        nombre = f"mermas_{anio}.pdf"

    html = render(request, 'reportes/mermas_pdf.html', {
        'mermas': mermas,
        'titulo': titulo
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre}"'

    HTML(string=html.content.decode('utf-8')).write_pdf(response)
    return response
