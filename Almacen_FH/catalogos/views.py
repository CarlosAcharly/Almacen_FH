from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages

from .models import (
    Proveedor, Cliente, Chofer, UnidadTransporte,
    Lugar, Categoria, Producto
)

from .forms import (
    ProveedorForm, ClienteForm, ChoferForm,
    UnidadForm, LugarForm, CategoriaForm, ProductoForm
)

# =========================
# PRODUCTOS
# =========================

def lista_productos(request):
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')
    per_page = int(request.GET.get('per_page', 15))

    productos = Producto.objects.select_related('categoria').filter(
        eliminado=False
    )

    if q:
        productos = productos.filter(nombre__icontains=q)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    productos = productos.order_by('nombre')

    paginator = Paginator(productos, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.all()

    return render(request, 'catalogos/productos/lista.html', {
        'page_obj': page_obj,
        'categorias': categorias,
        'q': q,
        'categoria_id': categoria_id,
        'per_page': per_page,
        'per_page_options': [15, 25, 40],
    })


def crear_producto(request):
    form = ProductoForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, 'Producto creado correctamente')
        return redirect('lista_productos')

    return render(request, 'catalogos/productos/crear.html', {
        'form': form
    })


def editar_producto(request, pk):
    producto = get_object_or_404(
        Producto,
        pk=pk,
        eliminado=False
    )

    form = ProductoForm(request.POST or None, instance=producto)

    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado')
        return redirect('lista_productos')

    return render(request, 'catalogos/productos/crear.html', {
        'form': form
    })


# 🗑 ENVIAR A PAPELERA
def eliminar_producto(request, pk):
    producto = get_object_or_404(
        Producto,
        pk=pk,
        eliminado=False
    )

    producto.eliminado = True
    producto.activo = False
    producto.fecha_eliminado = timezone.now()
    producto.save()

    messages.success(request, 'Producto enviado a la papelera')
    return redirect('lista_productos')


# 🧺 PAPELERA
def papelera_productos(request):
    productos = Producto.objects.select_related('categoria').filter(
        eliminado=True
    ).order_by('-fecha_eliminado')

    return render(request, 'catalogos/productos/papelera.html', {
        'productos': productos
    })


# ♻ RESTAURAR
def restaurar_producto(request, pk):
    producto = get_object_or_404(
        Producto,
        pk=pk,
        eliminado=True
    )

    producto.eliminado = False
    producto.activo = True
    producto.fecha_eliminado = None
    producto.save()

    messages.success(request, 'Producto restaurado correctamente')
    return redirect('papelera_productos')


# =========================
# PROVEEDORES
# =========================

def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'catalogos/proveedores/lista.html', {'proveedores': proveedores})


def crear_proveedor(request):
    form = ProveedorForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_proveedores')
    return render(request, 'catalogos/proveedores/crear.html', {'form': form})


def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(request.POST or None, instance=proveedor)
    if form.is_valid():
        form.save()
        return redirect('lista_proveedores')
    return render(request, 'catalogos/proveedores/crear.html', {'form': form})


def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.delete()
    return redirect('lista_proveedores')


# =========================
# CLIENTES
# =========================

def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'catalogos/clientes/lista.html', {'clientes': clientes})


def crear_cliente(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_clientes')
    return render(request, 'catalogos/clientes/crear.html', {'form': form})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        return redirect('lista_clientes')
    return render(request, 'catalogos/clientes/crear.html', {'form': form})


def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.delete()
    return redirect('lista_clientes')


# =========================
# CHOFERES
# =========================

def lista_choferes(request):
    choferes = Chofer.objects.all()
    return render(request, 'catalogos/choferes/lista.html', {'choferes': choferes})


def crear_chofer(request):
    form = ChoferForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_choferes')
    return render(request, 'catalogos/choferes/crear.html', {'form': form})


def editar_chofer(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    form = ChoferForm(request.POST or None, instance=chofer)
    if form.is_valid():
        form.save()
        return redirect('lista_choferes')
    return render(request, 'catalogos/choferes/crear.html', {'form': form})


def eliminar_chofer(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    chofer.delete()
    return redirect('lista_choferes')


# =========================
# UNIDADES
# =========================

def lista_unidades(request):
    unidades = UnidadTransporte.objects.all().order_by('-id')
    return render(request, 'catalogos/unidades/lista.html', {'unidades': unidades})


def crear_unidad(request):
    form = UnidadForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_unidades')
    return render(request, 'catalogos/unidades/crear.html', {'form': form})


def editar_unidad(request, pk):
    unidad = get_object_or_404(UnidadTransporte, pk=pk)
    form = UnidadForm(request.POST or None, instance=unidad)
    if form.is_valid():
        form.save()
        return redirect('lista_unidades')
    return render(request, 'catalogos/unidades/crear.html', {'form': form})


def eliminar_unidad(request, pk):
    unidad = get_object_or_404(UnidadTransporte, pk=pk)
    unidad.delete()
    return redirect('lista_unidades')


# =========================
# LUGARES
# =========================

def lista_lugares(request):
    lugares = Lugar.objects.all()
    return render(request, 'catalogos/lugares/lista.html', {'lugares': lugares})


def crear_lugar(request):
    form = LugarForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_lugares')
    return render(request, 'catalogos/lugares/crear.html', {'form': form})


def editar_lugar(request, pk):
    lugar = get_object_or_404(Lugar, pk=pk)
    form = LugarForm(request.POST or None, instance=lugar)
    if form.is_valid():
        form.save()
        return redirect('lista_lugares')
    return render(request, 'catalogos/lugares/crear.html', {'form': form})


def eliminar_lugar(request, pk):
    lugar = get_object_or_404(Lugar, pk=pk)
    lugar.delete()
    return redirect('lista_lugares')


# =========================
# CATEGORÍAS
# =========================

def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'catalogos/categorias/lista.html', {'categorias': categorias})


def crear_categoria(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_categorias')
    return render(request, 'catalogos/categorias/crear.html', {'form': form})


def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        return redirect('lista_categorias')
    return render(request, 'catalogos/categorias/crear.html', {'form': form})


def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    return redirect('lista_categorias')
