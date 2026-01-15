from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Dieta, DetalleDieta, PreparacionDieta
from .services import preparar_dieta
from .forms import DietaForm
from catalogos.models import Categoria, Producto


# =========================
# LISTA DE DIETAS (ACTIVAS)
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
@transaction.atomic
def crear_dieta(request):
    if request.method == 'POST':
        form = DietaForm(request.POST)
        if form.is_valid():
            
            # Verificar si ya existe dieta con este nombre (no eliminada)
            if Dieta.objects.filter(
                nombre=form.cleaned_data['nombre'],
                eliminada=False
            ).exists():
                messages.error(request, 'Ya existe una dieta con este nombre')
                return render(request, 'dietas/crear_dieta.html', {'form': form})
            
            # Crear producto para la dieta (stock inicial 0)
            categoria_dietas = get_object_or_404(
                Categoria,
                nombre='Dietas'
            )
            
            producto = Producto.objects.create(
                nombre=f"Dieta {form.cleaned_data['nombre']}",
                categoria=categoria_dietas,
                stock_kg=0,
                activo=True
            )
            
            # Crear dieta
            dieta = form.save(commit=False)
            dieta.producto_dieta = producto
            dieta.save()
            
            messages.success(request, 'Dieta creada correctamente')
            return redirect('editar_dieta', dieta_id=dieta.id)
    else:
        form = DietaForm()

    return render(request, 'dietas/crear_dieta.html', {
        'form': form
    })


# =========================
# EDITAR / GUARDAR DIETA
# =========================
@login_required
def editar_dieta(request, dieta_id):
    dieta = get_object_or_404(
        Dieta,
        id=dieta_id,
        eliminada=False
    )
    
    ingredientes = Producto.objects.filter(
        activo=True,
        categoria__nombre='Ingrediente de dieta'
    ).order_by('nombre')
    
    detalles_qs = DetalleDieta.objects.filter(dieta=dieta)
    detalles = {d.producto.id: d.kg for d in detalles_qs}
    
    # Calcular total actual
    total_actual = sum([float(kg) for kg in detalles.values()])
    
    if request.method == 'POST':
        # Verificar qué acción se está realizando
        if 'guardar_ingredientes' in request.POST:
            nuevo_total = 0
            
            for ingrediente in ingredientes:
                kg_str = request.POST.get(f'kg_{ingrediente.id}', '0').strip()
                kg = float(kg_str) if kg_str else 0
                
                if kg > 0:
                    DetalleDieta.objects.update_or_create(
                        dieta=dieta,
                        producto=ingrediente,
                        defaults={'kg': kg}
                    )
                    nuevo_total += kg
                else:
                    DetalleDieta.objects.filter(
                        dieta=dieta,
                        producto=ingrediente
                    ).delete()
            
            # Actualizar total de la dieta
            dieta.total_kg = nuevo_total
            dieta.save(update_fields=['total_kg'])
            
            messages.success(request, 'Ingredientes guardados correctamente')
            return redirect('editar_dieta', dieta_id=dieta.id)
        
        # Actualizar información básica de la dieta
        elif 'actualizar_info' in request.POST:
            form = DietaForm(request.POST, instance=dieta)
            if form.is_valid():
                form.save()
                messages.success(request, 'Información actualizada correctamente')
                return redirect('editar_dieta', dieta_id=dieta.id)
            else:
                messages.error(request, 'Error al actualizar la información')
    
    # Para GET request
    form = DietaForm(instance=dieta)
    
    # Obtener historial de preparaciones - CORREGIDO
    preparaciones = PreparacionDieta.objects.filter(dieta=dieta).order_by('-fecha_hora')[:10]
    
    return render(request, 'dietas/editar_dieta.html', {
        'dieta': dieta,
        'ingredientes': ingredientes,
        'detalles': detalles,
        'total_actual': total_actual,
        'form': form,
        'preparaciones': preparaciones
    })


# =========================
# PREPARAR DIETA
# =========================
@login_required
def preparar_dieta_view(request, dieta_id):
    if request.method != 'POST':
        return redirect('lista_dietas')
    
    dieta = get_object_or_404(
        Dieta,
        id=dieta_id,
        eliminada=False
    )
    
    # Verificar que la dieta tenga ingredientes
    if not dieta.detalles.exists():
        messages.error(request, 'La dieta no tiene ingredientes configurados')
        return redirect('lista_dietas')
    
    observaciones = request.POST.get('observaciones', '')
    
    try:
        cantidad_preparada = preparar_dieta(dieta, request.user, observaciones)
        
        messages.success(
            request,
            f'✅ Dieta "{dieta.nombre}" preparada correctamente. '
            f'Se produjeron {cantidad_preparada} kg'
        )
    except ValidationError as e:
        messages.error(request, f'❌ {str(e)}')
    except Exception as e:
        messages.error(request, f'❌ Error al preparar la dieta: {str(e)}')
    
    return redirect('lista_dietas')


# =========================
# PAPELERA DE DIETAS
# =========================
@login_required
def papelera_dietas(request):
    dietas = Dieta.objects.filter(
        eliminada=True
    ).order_by('-eliminada_en')

    return render(request, 'dietas/papelera.html', {
        'dietas': dietas
    })


# =========================
# RESTAURAR DIETA
# =========================
@login_required
def restaurar_dieta(request, dieta_id):
    if request.method != 'POST':
        return redirect('papelera_dietas')

    dieta = get_object_or_404(
        Dieta,
        id=dieta_id,
        eliminada=True
    )

    dieta.restaurar()

    messages.success(
        request,
        f'♻️ Dieta "{dieta.nombre}" restaurada correctamente'
    )
    return redirect('papelera_dietas')


# =========================
# ELIMINAR DIETA (SOFT DELETE)
# =========================
@login_required
def eliminar_dieta(request, dieta_id):
    if request.method != 'POST':
        return redirect('lista_dietas')

    dieta = get_object_or_404(
        Dieta,
        id=dieta_id,
        eliminada=False
    )

    dieta.eliminar()

    messages.warning(
        request,
        f'🗑️ La dieta "{dieta.nombre}" fue enviada a la papelera'
    )
    return redirect('lista_dietas')