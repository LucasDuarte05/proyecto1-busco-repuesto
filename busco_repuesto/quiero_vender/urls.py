from django.urls import path
from . import views

urlpatterns = [
    path('quiero-vender/', views.ver_solicitudes, name='ver_solicitudes'),
    path('login-vendedor/', views.login_vendedor, name='login_vendedor'),
    path('publicar-repuesto/', views.publicar_repuesto, name='publicar_repuesto'),
    path('procesar-publicacion/', views.procesar_publicacion, name='procesar_publicacion'),
    path('procesar-venta/', views.procesar_venta, name='procesar_venta'),
]