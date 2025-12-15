from django.urls import path
from . import views

urlpatterns = [
    path('quiero-vender/', views.ver_solicitudes, name='ver_solicitudes'),
    path('login-vendedor/', views.login_vendedor, name='login_vendedor'),
    path('logout-vendedor/', views.logout_vendedor, name='logout_vendedor'),
    path('publicar-repuesto/', views.publicar_repuesto, name='publicar_repuesto'),
    path('procesar-publicacion/', views.procesar_publicacion, name='procesar_publicacion'),
    path('procesar-venta/', views.procesar_venta, name='procesar_venta'),
    
    # ✅ AGREGAR ESTAS 2 RUTAS NUEVAS:
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),
    path('guardar-perfil/', views.guardar_perfil, name='guardar_perfil'),
    path('enviar-cotizacion/<int:solicitud_id>/', views.enviar_cotizacion, name='enviar_cotizacion'),
    

    path('admin/cotizaciones/', views.admin_cotizaciones, name='admin_cotizaciones'),
    path('admin/cotizacion/<int:cotizacion_id>/', views.detalle_cotizacion, name='detalle_cotizacion'),
    path('admin/vendedor/<int:vendedor_id>/', views.perfil_vendedor_admin, name='perfil_vendedor_admin'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/verificar/', views.admin_verificar, name='admin_verificar'),
    
    # Respuesta del cliente
    path('cliente/interes/<int:cotizacion_id>/', views.cliente_interes, name='cliente_interes'),


]