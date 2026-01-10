from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT)
    descripcion = models.TextField(blank=True)

    stock_kg = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    peso_por_bulto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Peso en kg de un bulto (solo si aplica)"
    )

    activo = models.BooleanField(default=True)

    # 🔥 PAPELERA
    eliminado = models.BooleanField(default=False)
    fecha_eliminado = models.DateTimeField(null=True, blank=True)

    def peso_bulto(self):
        return self.peso_por_bulto or 0

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre


class Lugar(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Chofer(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre


class UnidadTransporte(models.Model):
    marca = models.CharField(max_length=60)
    placa = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=40)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.marca} - {self.placa}"
