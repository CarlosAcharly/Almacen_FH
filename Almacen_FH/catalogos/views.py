from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Proveedor, Cliente, Chofer, UnidadTransporte, Lugar, Categoria, Producto
from .forms import ProveedorForm, ClienteForm, ChoferForm, UnidadTransporte, LugarForm, CategoriaForm, ProductoForm, UnidadForm 


# =========================
# LISTA + BUSCADOR + PAGINADOR
# =========================
def lista_productos(request):
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')
    per_page = int(request.GET.get('per_page', 15))

    productos = Producto.objects.select_related('categoria').all()

    # 🔍 Buscar por nombre
    if q:
        productos = productos.filter(nombre__icontains=q)

    # 🗂️ Filtrar por categoría
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    productos = productos.order_by('nombre')

    # 📄 Paginación
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


# =========================
# CREAR
# =========================
def crear_producto(request):
    form = ProductoForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('lista_productos')

    return render(request, 'catalogos/productos/crear.html', {
        'form': form
    })


# =========================
# EDITAR
# =========================
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)

    if form.is_valid():
        form.save()
        return redirect('lista_productos')

    return render(request, 'catalogos/productos/crear.html', {
        'form': form
    })


# =========================
# ELIMINAR
# =========================
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return redirect('lista_productos')

# PROVEEDORES
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'catalogos/proveedores/lista.html', {'proveedores': proveedores})

def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'catalogos/proveedores/crear.html', {'form': form})

def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'catalogos/proveedores/crear.html', {'form': form})

def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.delete()
    return redirect('lista_proveedores')

# CLIENTES
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'catalogos/clientes/lista.html', {'clientes': clientes})

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'catalogos/clientes/crear.html', {'form': form})

def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'catalogos/clientes/crear.html', {'form': form})

def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.delete()
    return redirect('lista_clientes')


#CHOFERES
def lista_choferes(request):
    choferes = Chofer.objects.all()
    return render(request, 'catalogos/choferes/lista.html', {'choferes': choferes})

def crear_chofer(request):
    if request.method == 'POST':
        form = ChoferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_choferes')
    else:
        form = ChoferForm()
    return render(request, 'catalogos/choferes/crear.html', {'form': form}) 

def editar_chofer(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    if request.method == 'POST':
        form = ChoferForm(request.POST, instance=chofer)
        if form.is_valid():
            form.save()
            return redirect('lista_choferes')
    else:
        form = ChoferForm(instance=chofer)
    return render(request, 'catalogos/choferes/crear.html', {'form': form})

def eliminar_chofer(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    chofer.delete()
    return redirect('lista_choferes')

# UNIDADES DE TRANSPORTE
# ----------------------------------------------
def lista_unidades(request):
    unidades = UnidadTransporte.objects.all()
    return render(request, 'catalogos/unidades/lista.html', {'unidades': unidades})

def crear_unidad(request):
    if request.method == 'POST':
        form = UnidadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_unidades')
    else:
        form = UnidadForm()
    return render(request, 'catalogos/unidades/crear.html', {'form': form})

def editar_unidad(request, pk):
    unidad = get_object_or_404(UnidadTransporte, pk=pk)
    if request.method == 'POST':
        form = UnidadForm(request.POST, instance=unidad)
        if form.is_valid():
            form.save()
            return redirect('lista_unidades')
    else:
        form = UnidadForm(instance=unidad)
    return render(request, 'catalogos/unidades/crear.html', {'form': form})

def eliminar_unidad(request, pk):
    unidad = get_object_or_404(UnidadTransporte, pk=pk)
    unidad.delete()
    return redirect('lista_unidades')

# LUGARES
def lista_lugares(request):
    lugares = Lugar.objects.all()
    return render(request, 'catalogos/lugares/lista.html', {'lugares': lugares})
def crear_lugar(request):
    if request.method == 'POST':
        form = LugarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_lugares')
    else:
        form = LugarForm()
    return render(request, 'catalogos/lugares/crear.html', {'form': form})
def editar_lugar(request, pk):
    lugar = get_object_or_404(Lugar, pk=pk)
    if request.method == 'POST':
        form = LugarForm(request.POST, instance=lugar)
        if form.is_valid():
            form.save()
            return redirect('lista_lugares')
    else:
        form = LugarForm(instance=lugar)
    return render(request, 'catalogos/lugares/crear.html', {'form': form})
def eliminar_lugar(request, pk):
    lugar = get_object_or_404(Lugar, pk=pk)
    lugar.delete()
    return redirect('lista_lugares')

# CATEGORIAS
# ----------------------------------------------
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'catalogos/categorias/lista.html', {'categorias': categorias})

def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'catalogos/categorias/crear.html', {'form': form})

def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'catalogos/categorias/crear.html', {'form': form})

def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    return redirect('lista_categorias')

