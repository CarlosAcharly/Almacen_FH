# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('ALMACEN', 'Almacenista'),
    )

    ESTADOS = (
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    )

    rol = models.CharField(max_length=10, choices=ROLES, default='ALMACEN')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Campos para auditoría
    creado_por = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='usuarios_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
        permissions = [
            ('puede_crear_usuario', 'Puede crear usuarios'),
            ('puede_editar_usuario', 'Puede editar usuarios'),
            ('puede_eliminar_usuario', 'Puede eliminar usuarios'),
        ]

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"

    @property
    def es_administrador(self):
        return self.rol == 'ADMIN'

    @property
    def es_almacenista(self):
        return self.rol == 'ALMACEN'

    def actualizar_ultimo_acceso(self):
        self.ultimo_acceso = timezone.now()
        self.save(update_fields=['ultimo_acceso'])