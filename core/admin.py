from django.contrib import admin
from .models import SolicitudCompra, PublicacionVenta, VendedorEmpresa, Cotizacion, ImagenRepuesto

class ImagenRepuestoInline(admin.TabularInline):
    model = ImagenRepuesto
    extra = 1
    readonly_fields = ['fecha_subida']

@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'repuesto_especifico', 'marca_auto', 'urgencia', 'fecha_solicitud', 'activa', 'get_num_imagenes']
    list_filter = ['activa', 'urgencia', 'categoria_repuesto', 'marca_auto']
    search_fields = ['nombre', 'repuesto_especifico', 'marca_auto', 'celular']
    date_hierarchy = 'fecha_solicitud'
    def get_num_imagenes(self, obj):
        return obj.imagenes.count()
    get_num_imagenes.short_description = 'Imágenes'

admin.site.register(ImagenRepuesto)

@admin.register(PublicacionVenta)
class PublicacionVentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_vendedor', 'zona', 'localidad', 'fecha_publicacion', 'disponible']
    list_filter = ['disponible', 'zona']
    search_fields = ['nombre_vendedor', 'email_vendedor', 'localidad']
    date_hierarchy = 'fecha_publicacion'


@admin.register(VendedorEmpresa)
class VendedorEmpresaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_empresa', 'cuit', 'user', 'provincia', 'localidad', 'activo', 'fecha_registro']
    list_filter = ['activo', 'provincia', 'fecha_registro']
    search_fields = ['nombre_empresa', 'cuit', 'user__email', 'user__first_name', 'user__last_name']
    date_hierarchy = 'fecha_registro'
    readonly_fields = ['fecha_registro']


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendedor', 'solicitud', 'precio', 'estado', 'fecha_creacion', 'fecha_envio']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['vendedor__nombre_empresa', 'solicitud__nombre', 'solicitud__repuesto_especifico']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ['fecha_creacion']
    
    def get_readonly_fields(self, request, obj=None):
        # Si la cotización ya existe, no permitir cambiar solicitud ni vendedor
        if obj:
            return self.readonly_fields + ['solicitud', 'vendedor']
        return self.readonly_fields