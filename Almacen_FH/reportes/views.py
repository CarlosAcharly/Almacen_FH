from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from decimal import Decimal

from movimientos.models import Entrada, Salida
from catalogos.models import Producto
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from decimal import Decimal
from movimientos.models import Salida

from movimientos.models import Entrada
from .utils import encabezado_pdf

from movimientos.models import Merma
from weasyprint import HTML


def total_kg_movimiento(mov):
    return (
        mov.kg +
        (mov.toneladas * Decimal('1000')) +
        (mov.bultos * mov.producto.peso_por_bulto)
    )


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

def total_kg_movimiento(mov):
    return (
        mov.kg +
        (mov.toneladas * Decimal('1000')) +
        (mov.bultos * mov.producto.peso_por_bulto)
    )


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

def pdf_salidas(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_salidas.pdf"'

    p = canvas.Canvas(response, pagesize=LETTER)
    encabezado_pdf(p, "Reporte de Salidas")

    y = 650
    p.setFont("Helvetica", 10)

    for s in Salida.objects.all().order_by('-fecha_hora'):
        total = (
            s.kg +
            (s.toneladas * 1000) +
            (s.bultos * s.producto.peso_por_bulto)
        )

        p.drawString(40, y, f"{s.fecha_hora.strftime('%d/%m/%Y')} - {s.producto.nombre}")
        p.drawString(240, y, f"{s.tipo}")
        p.drawString(340, y, f"{total} kg")
        y -= 20

        if y < 50:
            p.showPage()
            encabezado_pdf(p, "Reporte de Salidas")
            y = 650

    p.showPage()
    p.save()
    return response

def hoja_traslado(request, salida_id):
    salida = Salida.objects.get(id=salida_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="hoja_traslado.pdf"'

    p = canvas.Canvas(response, pagesize=LETTER)
    encabezado_pdf(p, "Hoja de Traslado")

    p.setFont("Helvetica", 11)
    y = 650

    p.drawString(40, y, f"Fecha: {salida.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
    y -= 30

    p.drawString(40, y, f"Producto: {salida.producto.nombre}")
    y -= 20

    p.drawString(40, y, f"Cantidad total (kg): {salida.kg + (salida.toneladas * 1000) + (salida.bultos * salida.producto.peso_por_bulto)}")
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

def reporte_mermas_pdf(request, anio, mes=None):
    if mes:
        mermas = Merma.objects.filter(
            fecha_hora__year=anio,
            fecha_hora__month=mes
        )
        titulo = f"Reporte de Mermas - {mes}/{anio}"
        nombre = f"mermas_{mes}_{anio}.pdf"
    else:
        mermas = Merma.objects.filter(fecha_hora__year=anio)
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