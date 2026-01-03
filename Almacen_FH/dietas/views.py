from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Dieta, DetalleDieta
from .services import preparar_dieta
from .forms import DietaForm
from catalogos.models import Categoria, Producto


@login_required
def lista_dietas(request):
    dietas = Dieta.objects.filter(activa=True)
    return render(request, 'dietas/lista.html', {
        'dietas': dietas
    })


@login_required
def crear_dieta(request):
    if request.method == 'POST':
        form = DietaForm(request.POST)
        if form.is_valid():

            # Crear producto automáticamente
            categoria_dietas = Categoria.objects.get(nombre='Dietas')

            producto = Producto.objects.create(
                nombre=form.cleaned_data['nombre'],
                categoria=categoria_dietas,
                stock_kg=0
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


@login_required
def editar_dieta(request, dieta_id):
    dieta = get_object_or_404(Dieta, id=dieta_id, activa=True)
    ingredientes = Producto.objects.filter(activo=True)

    detalles_qs = DetalleDieta.objects.filter(dieta=dieta)
    detalles = {d.producto.id: d.kg for d in detalles_qs}

    if request.method == 'POST':
        for ingrediente in ingredientes:
            kg = float(request.POST.get(f'kg_{ingrediente.id}', 0) or 0)

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


@login_required
def preparar_dieta_view(request, dieta_id):
    if request.method != 'POST':
        return redirect('editar_dieta', dieta_id)

    dieta = get_object_or_404(Dieta, id=dieta_id, activa=True)

    try:
        preparar_dieta(dieta, request.user)
        messages.success(
            request,
            f'Dieta "{dieta.nombre}" agregada al stock correctamente'
        )
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect('editar_dieta', dieta.id)
