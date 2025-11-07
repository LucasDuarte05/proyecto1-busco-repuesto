from django.contrib import admin
from .models import PublicacionVenta, SolicitudCompra


# --- ADMIN PARA PUBLICACIONES ---
@admin.register(PublicacionVenta)
class PublicacionVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'precio', 'disponible', 'categoria', 'fecha_publicacion')
    list_filter = ('disponible', 'categoria', 'estado', 'zona')
    search_fields = ('titulo', 'descripcion', 'marca_auto', 'modelo_auto', 'nombre_vendedor')
    ordering = ('-fecha_publicacion',)
    list_editable = ('disponible',)
    list_per_page = 25

    # --- Filtro personalizado: precios inválidos o vacíos ---
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si alguno tiene precio None o negativo, lo mostramos también
        for rep in qs:
            if rep.precio is None:
                print(f"⚠️ Publicación con precio None: {rep.titulo}")
        return qs


# --- ADMIN PARA SOLICITUDES DE COMPRA ---
@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'repuesto_especifico', 'urgencia', 'activa', 'fecha_solicitud')
    list_filter = ('urgencia', 'categoria_repuesto', 'activa')
    search_fields = ('nombre', 'email', 'repuesto_especifico', 'marca_auto', 'modelo_auto')
    ordering = ('-fecha_solicitud',)
    list_editable = ('activa',)
    list_per_page = 25
