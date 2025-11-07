from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import SolicitudCompra, PublicacionVenta
from django.db.models import Q



def login_vendedor(request):
    """Mostrar página de login para vendedores"""
    return render(request, 'login_vendedor.html')

def quiero_vender(request):
    """Mostrar opciones para vendedores"""
    return render(request, 'listado_solicitudes.html')

def publicar_repuesto(request):
    """Mostrar formulario para publicar repuesto"""
    return render(request, 'publicar_repuesto.html')

def procesar_publicacion(request):
    """Procesar publicación de repuesto y buscar solicitudes coincidentes"""
    if request.method == 'POST':
        try:
            # Obtener marca (puede ser del select o del campo "otro")
            marca_auto = request.POST.get('marca_auto')
            if marca_auto == 'Otro':
                marca_auto = request.POST.get('marca_auto_otro', '')
            
            # Obtener modelo (puede ser del select o del campo "otro")
            modelo_auto = request.POST.get('modelo_auto', '')
            if modelo_auto == 'Otro':
                modelo_auto = request.POST.get('modelo_auto_otro', '')
            
            # Obtener ubicación (puede ser del select o del campo "otro")
            ubicacion = request.POST.get('ubicacion')
            if ubicacion == 'Otro':
                ubicacion = request.POST.get('ubicacion_otro', '')
            
            # Obtener años (pueden ser vacíos)
            año_desde = request.POST.get('año_desde')
            año_hasta = request.POST.get('año_hasta')
            
            # Crear la publicación de venta
            publicacion = PublicacionVenta.objects.create(
                titulo=request.POST.get('titulo'),
                marca_auto=marca_auto,
                modelo_auto=modelo_auto,
                año_desde=int(año_desde) if año_desde else None,
                año_hasta=int(año_hasta) if año_hasta else None,
                categoria=request.POST.get('categoria'),
                descripcion=request.POST.get('descripcion'),
                estado=request.POST.get('estado'),
                precio=request.POST.get('precio'),
                ubicacion=ubicacion,
                nombre_vendedor=request.POST.get('nombre_vendedor'),
                email_vendedor=request.POST.get('email_vendedor'),
                telefono_vendedor=request.POST.get('telefono_vendedor')
            )
            
            # Buscar solicitudes que coincidan con este repuesto
            solicitudes_coincidentes = buscar_solicitudes_compatibles(publicacion)
            
            messages.success(request, '¡Tu repuesto ha sido publicado exitosamente!')
            
            context = {
                'publicacion': publicacion,
                'solicitudes': solicitudes_coincidentes,
                'total_solicitudes': solicitudes_coincidentes.count(),
                'hay_coincidencias': solicitudes_coincidentes.exists()
            }
            
            return render(request, 'confirmacion_publicacion.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al publicar el repuesto: {str(e)}')
            return redirect('publicar_repuesto')
    
    return redirect('publicar_repuesto')

def procesar_venta(request):
    """Alias para procesar_publicacion (mantener compatibilidad)"""
    return procesar_publicacion(request)

def ver_solicitudes(request):
    """Ver todas las solicitudes de compra activas"""
    solicitudes = SolicitudCompra.objects.filter(activa=True)
    
    # Obtener filtros de la URL
    marca_filtro = request.GET.get('marca', '')
    modelo_filtro = request.GET.get('modelo', '')
    categoria_filtro = request.GET.get('categoria', '')
    urgencia_filtro = request.GET.get('urgencia', '')
    año_filtro = request.GET.get('año', '')
    
    # Aplicar filtros
    if marca_filtro:
        solicitudes = solicitudes.filter(marca_auto__icontains=marca_filtro)
    
    if modelo_filtro:
        solicitudes = solicitudes.filter(modelo_auto__icontains=modelo_filtro)
    
    if categoria_filtro:
        solicitudes = solicitudes.filter(categoria_repuesto=categoria_filtro)
    
    if urgencia_filtro:
        solicitudes = solicitudes.filter(urgencia=urgencia_filtro)
    
    if año_filtro:
        solicitudes = solicitudes.filter(año_auto=int(año_filtro))
    
    solicitudes = solicitudes.order_by('-fecha_solicitud')
    
    # Obtener valores únicos para los filtros
    marcas_disponibles = SolicitudCompra.objects.filter(activa=True).values_list('marca_auto', flat=True).distinct().order_by('marca_auto')
    categorias_disponibles = SolicitudCompra.CATEGORIA_CHOICES
    urgencias_disponibles = SolicitudCompra.URGENCIA_CHOICES
    
    context = {
        'solicitudes': solicitudes,
        'total_solicitudes': solicitudes.count(),
        'marcas_disponibles': marcas_disponibles,
        'categorias_disponibles': categorias_disponibles,
        'urgencias_disponibles': urgencias_disponibles,
        # Filtros actuales
        'marca_actual': marca_filtro,
        'modelo_actual': modelo_filtro,
        'categoria_actual': categoria_filtro,
        'urgencia_actual': urgencia_filtro,
        'año_actual': año_filtro,
    }
    
    return render(request, 'listado_solicitudes.html', context)

def buscar_solicitudes_compatibles(publicacion):
    """
    Buscar solicitudes de compra que coincidan con un repuesto publicado
    """
    solicitudes = SolicitudCompra.objects.filter(activa=True)
    
    # 1. FILTRO POR CATEGORÍA (debe coincidir)
    solicitudes = solicitudes.filter(categoria_repuesto=publicacion.categoria)
    
    # 2. FILTRO POR MARCA
    if publicacion.marca_auto and publicacion.marca_auto.lower() != 'universal':
        solicitudes = solicitudes.filter(marca_auto__icontains=publicacion.marca_auto)
    
    # 3. FILTRO POR MODELO (opcional)
    if publicacion.modelo_auto:
        solicitudes = solicitudes.filter(
            Q(modelo_auto__icontains=publicacion.modelo_auto) |
            Q(modelo_auto='') |
            Q(modelo_auto__isnull=True)
        )
    
    # 4. FILTRO POR AÑO
    if publicacion.año_desde or publicacion.año_hasta:
        query = Q()
        
        if publicacion.año_desde and publicacion.año_hasta:
            # Repuesto con rango de años
            query = Q(año_auto__gte=publicacion.año_desde, año_auto__lte=publicacion.año_hasta)
        elif publicacion.año_desde:
            query = Q(año_auto__gte=publicacion.año_desde)
        elif publicacion.año_hasta:
            query = Q(año_auto__lte=publicacion.año_hasta)
        
        # Incluir también solicitudes sin año especificado
        query |= Q(año_auto__isnull=True)
        
        solicitudes = solicitudes.filter(query)
    
    return solicitudes.distinct().order_by('-fecha_solicitud')