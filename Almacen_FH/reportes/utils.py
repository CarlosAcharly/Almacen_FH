from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def encabezado_pdf(p, titulo):
    p.drawImage("media/logos/logo.jpg", 40, 720, width=75, height=75)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(180, 740, "ALMACÉN FORRAJERA HERNÁNDEZ")
    p.setFont("Helvetica", 12)
    p.drawString(180, 720, titulo)
