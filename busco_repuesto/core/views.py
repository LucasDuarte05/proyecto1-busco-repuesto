from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import SolicitudCompra, PublicacionVenta
from decimal import Decimal, InvalidOperation

# ==================== VISTAS DE COMPRA ====================

def quiero_comprar(request):
    """Mostrar formulario de búsqueda de repuestos"""
    return render(request, 'quiero_comprar.html')

def procesar_compra(request):
    """Procesar formulario de búsqueda y mostrar resultados"""
    if request.method == 'POST':
        try:
            # Obtener año, manejar vacío
            año_auto = request.POST.get('año_auto')
            if año_auto:
                try:
                    año_auto = int(año_auto)
                except (ValueError, TypeError):
                    año_auto = None
            else:
                año_auto = None
            
            # Crear la solicitud de compra SIN EMAIL
            solicitud = SolicitudCompra.objects.create(
                marca_auto=request.POST.get('marca_auto', ''),
                modelo_auto=request.POST.get('modelo_auto', ''),
                año_auto=año_auto,
                categoria_repuesto=request.POST.get('categoria_repuesto', ''),
                repuesto_especifico=request.POST.get('repuesto_especifico', ''),
                descripcion_adicional=request.POST.get('descripcion_adicional', ''),
                urgencia=request.POST.get('urgencia', 'baja'),
                nombre=request.POST.get('nombre', ''),
                celular=request.POST.get('celular', ''),
                localidad=request.POST.get('localidad', ''),
                zona=request.POST.get('zona', '')
            )
            
            # Buscar repuestos con algoritmo de coincidencia mejorado
            repuestos_disponibles = buscar_repuestos_compatibles(solicitud)
            
            context = {
                'solicitud': solicitud,
                'repuestos': repuestos_disponibles,
                'total_encontrados': len(repuestos_disponibles),
                'localidad': request.POST.get('localidad', 'Caseros'),
                'zona': request.POST.get('zona', 'Buenos Aires')
            }
            
            return render(request, 'resultados_comprar.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return redirect('quiero_comprar')
    
    return redirect('quiero_comprar')

def procesar_solicitud(request):
    """Procesar solicitud de repuesto y mostrar confirmación con coincidencias"""
    if request.method == 'POST':
        try:
            # Obtener año, manejar vacío
            año_auto = request.POST.get('año_auto')
            if año_auto:
                try:
                    año_auto = int(año_auto)
                except (ValueError, TypeError):
                    año_auto = None
            else:
                año_auto = None
            
            # Crear la solicitud de compra SIN EMAIL
            solicitud = SolicitudCompra.objects.create(
                marca_auto=request.POST.get('marca_auto', ''),
                modelo_auto=request.POST.get('modelo_auto', ''),
                año_auto=año_auto,
                categoria_repuesto=request.POST.get('categoria_repuesto', ''),
                repuesto_especifico=request.POST.get('repuesto_especifico', ''),
                descripcion_adicional=request.POST.get('descripcion_adicional', ''),
                urgencia=request.POST.get('urgencia', 'baja'),
                nombre=request.POST.get('nombre', ''),
                celular=request.POST.get('celular', ''),
                localidad=request.POST.get('localidad', ''),
                zona=request.POST.get('zona', '')
            )
            
            # Buscar repuestos que coincidan con la solicitud
            repuestos_disponibles = buscar_repuestos_compatibles(solicitud)
            
            messages.success(request, '¡Tu solicitud ha sido registrada exitosamente!')
            
            # Contexto común
            context = {
                'solicitud': solicitud,
                'repuestos': repuestos_disponibles,
                'total_encontrados': len(repuestos_disponibles),
                'hay_coincidencias': len(repuestos_disponibles) > 0,
                'localidad': request.POST.get('localidad', 'Caseros'),
                'zona': request.POST.get('zona', 'Buenos Aires')
            }
            
            return render(request, 'confirmacion_solicitud.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return redirect('quiero_comprar')

    return redirect('quiero_comprar')

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
            # Si no, mantener todos los de la categoría
            if repuestos_marca.exists():
                repuestos = repuestos_marca
                print(f"[DEBUG] Después de filtrar por marca '{solicitud.marca_auto}': {repuestos.count()}")
        
        # 4. FILTRO OPCIONAL POR MODELO (no eliminar si no coincide)
        if solicitud.modelo_auto:
            repuestos_modelo = repuestos.filter(
                Q(modelo_auto__icontains=solicitud.modelo_auto) |
                Q(modelo_auto='') |
                Q(modelo_auto__isnull=True)
            )
            
            # Solo aplicar si hay resultados
            if repuestos_modelo.exists():
                repuestos = repuestos_modelo
                print(f"[DEBUG] Después de filtrar por modelo '{solicitud.modelo_auto}': {repuestos.count()}")
        
        # 5. FILTRO FLEXIBLE POR AÑO
        if solicitud.año_auto:
            año = solicitud.año_auto
            repuestos_año = repuestos.filter(
                Q(
                    # El año está dentro del rango
                    (Q(año_desde__lte=año) | Q(año_desde__isnull=True)) &
                    (Q(año_hasta__gte=año) | Q(año_hasta__isnull=True))
                ) |
                Q(
                    # Sin año especificado (compatible con todos)
                    año_desde__isnull=True,
                    año_hasta__isnull=True
                )
            )
            
            # Solo aplicar si hay resultados
            if repuestos_año.exists():
                repuestos = repuestos_año
                print(f"[DEBUG] Después de filtrar por año {año}: {repuestos.count()}")
        
        # 6. BÚSQUEDA FLEXIBLE POR TÍTULO (NO OBLIGATORIA)
        # NO eliminar repuestos si no coincide el título
        # Solo destacar los que sí coinciden
        if solicitud.repuesto_especifico:
            palabras = solicitud.repuesto_especifico.split()
            query = Q()
            for palabra in palabras:
                if len(palabra) > 3:
                    query |= Q(titulo__icontains=palabra) | Q(descripcion__icontains=palabra)
            
            if query:
                repuestos_titulo = repuestos.filter(query)
                # Solo aplicar si hay resultados
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
        return []