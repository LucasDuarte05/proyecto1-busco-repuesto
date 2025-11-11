from django.urls import path
from . import views

urlpatterns = [
    path('quiero-comprar/', views.quiero_comprar, name='quiero_comprar'),
    path('procesar-solicitud/', views.procesar_compra, name='procesar_solicitud'),  # ✅ Esta debe apuntar a procesar_compra
    path('listado-repuestos/', views.listado_repuestos, name='listado_repuestos'),
]