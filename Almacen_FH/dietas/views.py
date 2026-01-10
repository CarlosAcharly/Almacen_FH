from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Dieta, DetalleDieta
from .services import preparar_dieta
from .forms import DietaForm
from catalogos.models import Categoria, Producto


# =========================
# LISTA DE DIETAS (activas)
# =========================
@login_required
def lista_dietas(request):
    dietas = Dieta.objects.filter(
        eliminada=False
    ).order_by('-fecha_creacion')

    return render(request, 'dietas/lista.html', {
        'dietas': dietas
    })


# =========================
# CREAR DIETA
# =========================
@login_required
def crear_dieta(request):
    if request.method == 'POST':
        form = DietaForm(request.POST)
        if form.is_valid():

            # 🔹 Categoría Dietas (producto terminado)
            categoria_dietas = get_object_or_404(
                Categoria,
                nombre='Dietas'
            )

            # 🔹 Crear producto automáticamente
            producto = Producto.objects.create(
                nombre=form.cleaned_data['nombre'],
                categoria=categoria_dietas,
                stock_kg=0,
                activo=True
            )

            dieta = form.save(commit=False)
            dieta.producto_dieta = producto
            dieta.save()

            messages.success(request, 'Dieta creada correctamente')
            return redirect('editar_dieta', dieta.id)
    else:
        form = DietaForm()

    return render(request, 'dietas/crear_dieta.html', {
        'form': form
    })


# =========================
# EDITAR DIETA
# =========================
@login_required
def editar_dieta(request, dieta_id):
    dieta = get_object_or_404(
        Dieta,
        id=dieta_id,
        eliminada=False
    )

    # ✅ SOLO INGREDIENTES DE DIETA
    ingredientes = Producto.objects.filter(
        activo=True,
        categoria__nombre='Ingrediente de dieta'
    ).order_by('nombre')

    detalles_qs = DetalleDieta.objects.filter(dieta=dieta)
    detalles = {d.producto.id: d.kg for d in detalles_qs}

    if request.method == 'POST':
        for ingrediente in ingredientes:
            kg = float(request.POST.get(
                f'kg_{ingrediente.id}', 0
            ) or 0)

            if kg > 0:
                DetalleDieta.objects.update_or_create(
                    dieta=dieta,
                    producto=ingrediente,
                    defaults={'kg': kg}
                )
            else:
                DetalleDieta.objects.filter(
                    dieta=dieta,
                    producto=ingrediente
                ).delete()

        dieta.recalcular_total()
        messages.success(request, "Dieta guardada correctamente")
        return redirect('editar_dieta', dieta.id)

    return render(request, 'dietas/editar_dieta.html', {
        'dieta': dieta,
        'ingredientes': ingredientes,
        'detalles': detalles
    })


# =========================
# ELIMINAR DIETA (PAPELERA)
# =========================
@login_required
def eliminar_dieta(request, dieta_id):
    dieta = get_object_or_404(Dieta, id=dieta_id, eliminada=False)

    dieta.eliminar()
    messages.warning(
        request,
        f'La dieta "{dieta.nombre}" fue enviada a la papelera'
    )

    return redirect('lista_dietas')


# =========================
# PREPARAR DIETA
# =========================
@login_required
def preparar_dieta_view(request, dieta_id):
    if request.method != 'POST':
        return redirect('editar_dieta', dieta_id)

    dieta = get_object_or_404(
        Dieta,
        id=dieta_id,
        eliminada=False
    )

    try:
        preparar_dieta(dieta, request.user)
        messages.success(
            request,
            f'Dieta "{dieta.nombre}" agregada al stock correctamente'
        )
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect('editar_dieta', dieta.id)

# =========================
# PAPELERA DE DIETAS
# =========================
@login_required
def papelera_dietas(request):
    dietas = Dieta.objects.filter(
        eliminada=True
    ).order_by('-fecha_creacion')

    return render(request, 'dietas/papelera.html', {
        'dietas': dietas
    })


# =========================
# RESTAURAR DIETA
# =========================
@login_required
def restaurar_dieta(request, dieta_id):
    dieta = get_object_or_404(Dieta, id=dieta_id, activa=False)
    dieta.activa = True
    dieta.save(update_fields=['activa'])

    messages.success(request, f'Dieta "{dieta.nombre}" restaurada correctamente')
    return redirect('papelera_dietas')

@login_required
def eliminar_dieta(request, dieta_id):
    if request.method != 'POST':
        return redirect('lista_dietas')

    dieta = get_object_or_404(Dieta, id=dieta_id, eliminada=False)
    dieta.eliminada = True
    dieta.save(update_fields=['eliminada'])

    messages.warning(request, 'Dieta enviada a la papelera')
    return redirect('lista_dietas')