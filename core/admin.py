from django.contrib import admin
from .models import PublicacionVenta, SolicitudCompra


# --- ADMIN PARA PUBLICACIONES ---
@admin.register(PublicacionVenta)
class PublicacionVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_vendedor', 'fecha_publicacion', 'disponible')
    list_filter = ('zona', 'disponible')  # ✅ Ahora es una tupla
    search_fields = ('nombre_vendedor', 'direccion', 'ubicacion')
    ordering = ('-fecha_publicacion',)
    list_editable = ('disponible',)  # ✅ 'disponible' ahora está en list_display
    list_per_page = 25


# --- ADMIN PARA SOLICITUDES DE COMPRA ---
@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'repuesto_especifico', 'urgencia', 'activa', 'fecha_solicitud')
    list_filter = ('urgencia', 'categoria_repuesto', 'activa')
    search_fields = ('nombre', 'email', 'repuesto_especifico', 'marca_auto', 'modelo_auto')
    ordering = ('-fecha_solicitud',)
    list_editable = ('activa',)
    list_per_page = 25