from django.contrib import admin
from .models import SolicitudCompra, PublicacionVenta

@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'repuesto_especifico', 'marca_auto', 'modelo_auto', 'urgencia', 'fecha_solicitud', 'activa')
    list_filter = ('urgencia', 'categoria_repuesto', 'marca_auto', 'activa', 'fecha_solicitud')
    search_fields = ('nombre_completo', 'repuesto_especifico', 'marca_auto', 'modelo_auto', 'email', 'telefono', 'dni')
    date_hierarchy = 'fecha_solicitud'
    ordering = ('-fecha_solicitud',)
    
    fieldsets = (
        ('Información del Vehículo y Repuesto', {
            'fields': ('marca_auto', 'modelo_auto', 'año_auto', 'categoria_repuesto', 'repuesto_especifico', 'descripcion_adicional', 'urgencia')
        }),
        ('Datos del Comprador', {
            'fields': ('nombre_completo', 'email', 'telefono', 'dni')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )
    
    readonly_fields = ('fecha_solicitud',)


@admin.register(PublicacionVenta)
class PublicacionVentaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'marca_auto', 'modelo_auto', 'categoria', 'estado', 'precio', 'ubicacion', 'nombre_vendedor', 'disponible', 'fecha_publicacion')
    list_filter = ('categoria', 'estado', 'marca_auto', 'disponible', 'fecha_publicacion')
    search_fields = ('titulo', 'marca_auto', 'modelo_auto', 'descripcion', 'nombre_vendedor', 'email_vendedor', 'telefono_vendedor')
    date_hierarchy = 'fecha_publicacion'
    ordering = ('-fecha_publicacion',)
    
    fieldsets = (
        ('Información del Repuesto', {
            'fields': ('titulo', 'categoria', 'descripcion', 'estado', 'precio')
        }),
        ('Compatibilidad', {
            'fields': ('marca_auto', 'modelo_auto', 'año_desde', 'año_hasta')
        }),
        ('Datos del Vendedor', {
            'fields': ('nombre_vendedor', 'email_vendedor', 'telefono_vendedor', 'ubicacion')
        }),
        ('Estado y Estadísticas', {
            'fields': ('disponible', 'vistas')
        }),
    )
    
    readonly_fields = ('fecha_publicacion', 'vistas')