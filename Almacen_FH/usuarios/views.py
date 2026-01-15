# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from .models import Usuario
from .forms import UsuarioRegistroForm, UsuarioEditarForm, PerfilEditarForm, CambiarContrasenaForm

# Decorador personalizado para verificar si es administrador
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Permitir tanto administradores como superusuarios
        if not (request.user.es_administrador or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para acceder a esta sección')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def perfil_usuario(request):
    """Perfil del usuario actual"""
    usuario = request.user
    
    # Actualizar último acceso
    if hasattr(usuario, 'actualizar_ultimo_acceso'):
        usuario.actualizar_ultimo_acceso()
    
    if request.method == 'POST':
        form = PerfilEditarForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil_usuario')
    else:
        form = PerfilEditarForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': 'Mi Perfil'
    }
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def cambiar_mi_contrasena(request):
    """Cambiar la contraseña del usuario actual"""
    if request.method == 'POST':
        form = CambiarContrasenaForm(request.POST)
        if form.is_valid():
            nueva_contrasena = form.cleaned_data['nueva_contrasena']
            request.user.set_password(nueva_contrasena)
            request.user.save()
            
            # Actualizar sesión para no cerrar sesión
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Contraseña actualizada exitosamente.')
            return redirect('perfil_usuario')
    else:
        form = CambiarContrasenaForm()
    
    context = {
        'form': form,
        'titulo': 'Cambiar Mi Contraseña'
    }
    
    return render(request, 'usuarios/cambiar_mi_contrasena.html', context)


@login_required
@admin_required
def lista_usuarios(request):
    """Lista todos los usuarios (solo para administradores)"""
    query = request.GET.get('q', '')
    rol_filter = request.GET.get('rol', '')
    estado_filter = request.GET.get('estado', '')
    
    usuarios = Usuario.objects.all()
    
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if rol_filter:
        usuarios = usuarios.filter(rol=rol_filter)
    
    if estado_filter:
        usuarios = usuarios.filter(estado=estado_filter)
    
    # Paginación - usa date_joined si fecha_creacion no existe
    try:
        usuarios = usuarios.order_by('-fecha_creacion')
    except:
        usuarios = usuarios.order_by('-date_joined')
    
    paginator = Paginator(usuarios, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'q': query,
        'rol_filter': rol_filter,
        'estado_filter': estado_filter,
        'roles': Usuario.ROLES,
        'estados': Usuario.ESTADOS,
        'total_usuarios': usuarios.count(),
        'total_activos': usuarios.filter(estado='ACTIVO').count(),
        'total_administradores': usuarios.filter(rol='ADMIN').count(),
        'total_almacenistas': usuarios.filter(rol='ALMACEN').count(),
    }
    
    return render(request, 'usuarios/lista.html', context)


@login_required
@admin_required
def crear_usuario(request):
    """Crear un nuevo usuario (solo para administradores)"""
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            # Guardar el usuario con el administrador que lo creó
            usuario = form.save(creado_por=request.user)
            
            messages.success(
                request,
                f'Usuario "{usuario.username}" creado exitosamente.'
            )
            
            # Generar credenciales para mostrar
            request.session['nuevo_usuario'] = {
                'username': usuario.username,
                'password': form.cleaned_data['password1'],
                'nombre_completo': f"{usuario.first_name} {usuario.last_name}",
                'rol': usuario.get_rol_display(),
                'email': usuario.email
            }
            
            return redirect('credenciales_usuario')
    else:
        form = UsuarioRegistroForm(initial={'rol': 'ALMACEN'})
    
    context = {
        'form': form,
        'titulo': 'Registrar Nuevo Usuario',
        'modo': 'crear'
    }
    
    return render(request, 'usuarios/formulario.html', context)


@login_required
@admin_required
def credenciales_usuario(request):
    """Mostrar credenciales del usuario recién creado"""
    nuevo_usuario = request.session.get('nuevo_usuario')
    
    if not nuevo_usuario:
        messages.warning(request, 'No hay credenciales para mostrar')
        return redirect('lista_usuarios')
    
    # Limpiar la sesión después de mostrar
    del request.session['nuevo_usuario']
    
    return render(request, 'usuarios/credenciales.html', {
        'usuario': nuevo_usuario
    })


@login_required
@admin_required
def editar_usuario(request, usuario_id):
    """Editar un usuario existente (solo para administradores)"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Evitar que un usuario se edite a sí mismo para cambiar rol/estado
    if usuario == request.user:
        messages.warning(request, 'No puedes editar tu propio perfil desde aquí. Usa la opción de perfil.')
        return redirect('lista_usuarios')
    
    if request.method == 'POST':
        form = UsuarioEditarForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.username}" actualizado exitosamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioEditarForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': f'Editar Usuario: {usuario.username}',
        'modo': 'editar'
    }
    
    return render(request, 'usuarios/formulario.html', context)


@login_required
@admin_required
def cambiar_contrasena(request, usuario_id):
    """Cambiar contraseña de un usuario (solo para administradores)"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        form = CambiarContrasenaForm(request.POST)
        if form.is_valid():
            nueva_contrasena = form.cleaned_data['nueva_contrasena']
            usuario.set_password(nueva_contrasena)
            usuario.save()
            
            # Guardar la nueva contraseña en sesión para mostrar
            request.session['nueva_contrasena'] = {
                'username': usuario.username,
                'password': nueva_contrasena,
                'nombre_completo': f"{usuario.first_name} {usuario.last_name}"
            }
            
            messages.success(request, f'Contraseña de "{usuario.username}" actualizada exitosamente.')
            return redirect('mostrar_contrasena')
    else:
        form = CambiarContrasenaForm()
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': f'Cambiar Contraseña: {usuario.username}'
    }
    
    return render(request, 'usuarios/cambiar_contrasena.html', context)


@login_required
@admin_required
def mostrar_contrasena(request):
    """Mostrar la nueva contraseña generada"""
    nueva_contrasena = request.session.get('nueva_contrasena')
    
    if not nueva_contrasena:
        messages.warning(request, 'No hay contraseña para mostrar')
        return redirect('lista_usuarios')
    
    # Limpiar la sesión después de mostrar
    del request.session['nueva_contrasena']
    
    return render(request, 'usuarios/mostrar_contrasena.html', {
        'usuario': nueva_contrasena
    })


@login_required
@admin_required
def cambiar_estado_usuario(request, usuario_id):
    """Activar/Desactivar un usuario (solo para administradores)"""
    if request.method != 'POST':
        return redirect('lista_usuarios')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Evitar que un usuario cambie su propio estado
    if usuario == request.user:
        messages.error(request, 'No puedes cambiar tu propio estado')
        return redirect('lista_usuarios')
    
    if usuario.estado == 'ACTIVO':
        usuario.estado = 'INACTIVO'
        mensaje = f'Usuario "{usuario.username}" desactivado'
        tipo = 'warning'
    else:
        usuario.estado = 'ACTIVO'
        mensaje = f'Usuario "{usuario.username}" activado'
        tipo = 'success'
    
    usuario.save()
    messages.add_message(request, messages.__dict__[tipo.upper()], mensaje)
    
    return redirect('lista_usuarios')


@login_required
@admin_required
def eliminar_usuario(request, usuario_id):
    """Eliminar un usuario (solo para administradores)"""
    if request.method != 'POST':
        return redirect('lista_usuarios')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Evitar que un usuario se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario')
        return redirect('lista_usuarios')
    
    # Evitar eliminar el último administrador
    if usuario.es_administrador and Usuario.objects.filter(rol='ADMIN').count() <= 1:
        messages.error(request, 'No puedes eliminar al único administrador')
        return redirect('lista_usuarios')
    
    username = usuario.username
    usuario.delete()
    
    messages.success(request, f'Usuario "{username}" eliminado exitosamente.')
    return redirect('lista_usuarios')