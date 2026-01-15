from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

@transaction.atomic
def preparar_dieta(request, dieta_id):
    dieta = get_object_or_404(Dieta, id=dieta_id)

    detalles = dieta.detalles.select_related('ingrediente')

    if not detalles.exists():
        messages.error(request, "La dieta no tiene ingredientes.")
        return redirect('lista_dietas')

    # VALIDAR STOCK
    for d in detalles:
        if d.ingrediente.stock_kg < d.kg:
            messages.error(
                request,
                f"Stock insuficiente de {d.ingrediente.nombre}"
            )
            return redirect('lista_dietas')

    # DESCONTAR STOCK
    for d in detalles:
        ingrediente = d.ingrediente
        ingrediente.stock_kg -= d.kg
        ingrediente.save()

    messages.success(
        request,
        f"Dieta '{dieta.nombre}' preparada correctamente"
    )

    return redirect('lista_dietas')
