from django.urls import path
from . import views

urlpatterns = [
    path('quiero-comprar/', views.quiero_comprar, name='quiero_comprar'),
    path('procesar-compra/', views.procesar_compra, name='procesar_compra'),
    path('procesar-solicitud/', views.procesar_solicitud, name='procesar_solicitud'),
    path('listado-repuestos/', views.listado_repuestos, name='listado_repuestos'),
]