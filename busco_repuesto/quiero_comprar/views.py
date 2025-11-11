from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import SolicitudCompra, PublicacionVenta
from decimal import Decimal, InvalidOperation
import json

# ==================== VISTAS DE COMPRA ====================

def quiero_comprar(request):
    """Mostrar formulario de búsqueda de repuestos"""
    return render(request, 'quiero_comprar.html')


def procesar_compra(request):
    """
    ✅ FUNCIÓN PRINCIPAL - Procesar solicitud y mostrar confirmación
    """
    if request.method != 'POST':
        return redirect('quiero_comprar')
    
    try:
        print("[DEBUG] Datos POST:", dict(request.POST))
        
        # Obtener año, manejar vacío
        año_auto = request.POST.get('año_auto')
        if año_auto:
            try:
                año_auto = int(año_auto)
            except (ValueError, TypeError):
                año_auto = None
        else:
            año_auto = None
        
        # ✅ Crear la solicitud de compra
        solicitud = SolicitudCompra.objects.create(
            marca_auto=request.POST.get('marca_auto', ''),
            modelo_auto=request.POST.get('modelo_auto', ''),
            año_auto=año_auto,
            nro_chasis=request.POST.get('nro_chasis', ''),
            categoria_repuesto=request.POST.get('categoria_repuesto', ''),
            repuesto_especifico=request.POST.get('repuesto_especifico', ''),
            descripcion_adicional=request.POST.get('descripcion_adicional', ''),
            urgencia=request.POST.get('urgencia', 'baja'),
            nombre=request.POST.get('nombre', ''),
            celular=request.POST.get('celular', ''),
            localidad=request.POST.get('localidad', ''),
            zona=request.POST.get('zona', '')
        )
        
        print(f"[INFO] Solicitud creada: ID {solicitud.id}")
        
        # Buscar repuestos que coincidan
        repuestos_disponibles = buscar_repuestos_compatibles(solicitud)
        
        # Agrupar repuestos por vendedor y preparar para el mapa
        vendedores_dict = {}
        for repuesto in repuestos_disponibles:
            vendedor_key = f"{repuesto.nombre_vendedor}_{repuesto.email_vendedor}"
            
            if vendedor_key not in vendedores_dict:
                vendedores_dict[vendedor_key] = {
                    'nombre': repuesto.nombre_vendedor,
                    'email': repuesto.email_vendedor,
                    'telefono': repuesto.telefono_vendedor,
                    'localidad': repuesto.localidad,
                    'zona': repuesto.zona,
                    'direccion': repuesto.direccion,
                    'latitud': float(repuesto.latitud) if repuesto.latitud else None,
                    'longitud': float(repuesto.longitud) if repuesto.longitud else None,
                    'tiene_gps': bool(repuesto.latitud and repuesto.longitud),
                    'repuestos_count': 0
                }
            
            vendedores_dict[vendedor_key]['repuestos_count'] += 1
        
        vendedores_list = list(vendedores_dict.values())
        vendedores_json = json.dumps(vendedores_list, ensure_ascii=False)
        
        print(f"[INFO] Encontrados {len(repuestos_disponibles)} repuestos de {len(vendedores_list)} vendedores")
        
        messages.success(request, '¡Tu solicitud ha sido registrada exitosamente!')
        
        context = {
            'solicitud': solicitud,
            'repuestos': repuestos_disponibles,
            'total_encontrados': len(repuestos_disponibles),
            'hay_coincidencias': len(repuestos_disponibles) > 0,
            'vendedores_list': vendedores_list,
            'vendedores_json': vendedores_json,
            'localidad': request.POST.get('localidad', ''),
            'zona': request.POST.get('zona', '')
        }
        
        # ✅ SIEMPRE retornar HttpResponse
        return render(request, 'confirmacion_solicitud.html', context)
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Error en procesar_compra: {str(e)}")
        traceback.print_exc()
        messages.error(request, f'Error al procesar la solicitud: {str(e)}')
        return redirect('quiero_comprar')


def procesar_solicitud(request):
    """
    ✅ FUNCIÓN ALTERNATIVA (redirige a procesar_compra)
    """
    return procesar_compra(request)


def listado_repuestos(request):
    """Mostrar todos los repuestos disponibles"""
    try:
        # Obtener todos los repuestos disponibles
        repuestos = PublicacionVenta.objects.filter(disponible=True)
        
        # Filtrar manualmente los que tienen precio válido
        repuestos_validos = []
        for repuesto in repuestos:
            try:
                precio = repuesto.precio
                if precio is not None and precio != '':
                    repuestos_validos.append(repuesto)
            except (ValueError, InvalidOperation, TypeError):
                continue
        
        context = {
            'repuestos': repuestos_validos,
            'total_repuestos': len(repuestos_validos)
        }
        return render(request, 'listado_repuestos.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar los repuestos: {str(e)}')
        context = {
            'repuestos': [],
            'total_repuestos': 0
        }
        return render(request, 'listado_repuestos.html', context)


# ==================== FUNCIONES AUXILIARES ====================

def buscar_repuestos_compatibles(solicitud):
    """
    Algoritmo de búsqueda MEJORADO con filtros más flexibles
    Prioriza coincidencias pero no descarta repuestos compatibles
    """
    try:
        # 1. COMENZAR CON TODOS LOS REPUESTOS DISPONIBLES
        repuestos = PublicacionVenta.objects.filter(disponible=True)
        
        print(f"[DEBUG] Total repuestos disponibles: {repuestos.count()}")
        
        # 2. FILTRO OBLIGATORIO: CATEGORÍA
        repuestos = repuestos.filter(categoria=solicitud.categoria_repuesto)
        print(f"[DEBUG] Después de filtrar por categoría '{solicitud.categoria_repuesto}': {repuestos.count()}")
        
        # 3. FILTRO FLEXIBLE POR MARCA
        if solicitud.marca_auto:
            # Buscar coincidencias exactas, parciales o universales
            repuestos_marca = repuestos.filter(
                Q(marca_auto__iexact=solicitud.marca_auto) |  # Exacta
                Q(marca_auto__icontains=solicitud.marca_auto) |  # Parcial
                Q(marca_auto__icontains='Universal') |  # Universal
                Q(marca_auto__icontains='Todos') |  # Todos
                Q(marca_auto='')  # Sin especificar (compatible con todos)
            )
            
            # Si hay resultados con filtro de marca, usarlos
            if repuestos_marca.exists():
                repuestos = repuestos_marca
                print(f"[DEBUG] Después de filtrar por marca '{solicitud.marca_auto}': {repuestos.count()}")
        
        # 4. FILTRO OPCIONAL POR MODELO
        if solicitud.modelo_auto:
            repuestos_modelo = repuestos.filter(
                Q(modelo_auto__icontains=solicitud.modelo_auto) |
                Q(modelo_auto='') |
                Q(modelo_auto__isnull=True)
            )
            
            if repuestos_modelo.exists():
                repuestos = repuestos_modelo
                print(f"[DEBUG] Después de filtrar por modelo '{solicitud.modelo_auto}': {repuestos.count()}")
        
        # 5. FILTRO FLEXIBLE POR AÑO
        if solicitud.año_auto:
            año = solicitud.año_auto
            repuestos_año = repuestos.filter(
                Q(
                    (Q(año_desde__lte=año) | Q(año_desde__isnull=True)) &
                    (Q(año_hasta__gte=año) | Q(año_hasta__isnull=True))
                ) |
                Q(
                    año_desde__isnull=True,
                    año_hasta__isnull=True
                )
            )
            
            if repuestos_año.exists():
                repuestos = repuestos_año
                print(f"[DEBUG] Después de filtrar por año {año}: {repuestos.count()}")
        
        # 6. BÚSQUEDA FLEXIBLE POR TÍTULO
        if solicitud.repuesto_especifico:
            palabras = solicitud.repuesto_especifico.split()
            query = Q()
            for palabra in palabras:
                if len(palabra) > 3:
                    query |= Q(titulo__icontains=palabra) | Q(descripcion__icontains=palabra)
            
            if query:
                repuestos_titulo = repuestos.filter(query)
                if repuestos_titulo.exists():
                    repuestos = repuestos_titulo
                    print(f"[DEBUG] Después de filtrar por título/descripción: {repuestos.count()}")
        
        # 7. CONVERTIR A LISTA Y VALIDAR PRECIOS
        repuestos_lista = list(repuestos.distinct().order_by('-fecha_publicacion'))
        repuestos_validos = []
        
        for repuesto in repuestos_lista:
            try:
                precio = repuesto.precio
                if precio is not None and precio != '':
                    repuestos_validos.append(repuesto)
            except (ValueError, InvalidOperation, TypeError):
                continue
        
        print(f"[DEBUG] Total repuestos válidos finales: {len(repuestos_validos)}")
        return repuestos_validos
        
    except Exception as e:
        print(f"[ERROR] Error en buscar_repuestos_compatibles: {str(e)}")
        import traceback
        traceback.print_exc()
        return []