from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from core.models import SolicitudCompra, PublicacionVenta
from django.db.models import Q
import requests
import time


def logout_vendedor(request):
    """Cerrar sesión del vendedor"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('index')


def login_vendedor(request):
    """Mostrar página de login para vendedores"""
    if request.user.is_authenticated:
        return redirect('ver_solicitudes')
    return render(request, 'login_vendedor.html')


@login_required(login_url='login_vendedor')
def ver_solicitudes(request):
    """Ver todas las solicitudes de compra activas - requiere login"""
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
        'marca_actual': marca_filtro,
        'modelo_actual': modelo_filtro,
        'categoria_actual': categoria_filtro,
        'urgencia_actual': urgencia_filtro,
        'año_actual': año_filtro,
        'usuario': request.user,
    }
    
    return render(request, 'listado_solicitudes.html', context)


def geocodificar_direccion(direccion, localidad, zona):
    """
    Convierte una dirección en coordenadas GPS usando Nominatim (OpenStreetMap)
    
    Args:
        direccion: calle y número (ej: "Escultor Santiago Parodi 5251")
        localidad: ciudad/localidad (ej: "Tres de Febrero")
        zona: provincia (ej: "Buenos Aires")
    
    Returns:
        tuple: (latitud, longitud) o (None, None) si falla
    """
    try:
        # Construir dirección completa
        direccion_completa = f"{direccion}, {localidad}, {zona}, Argentina"
        
        # API de Nominatim (gratuita)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': direccion_completa,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'ar'  # Solo Argentina
        }
        
        headers = {
            'User-Agent': 'BuscoRepuesto/1.0'  # Nominatim requiere User-Agent
        }
        
        print(f"[GEOCODING] Buscando: {direccion_completa}")
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(f"[GEOCODING] ✓ Encontrado: lat={lat}, lon={lon}")
                return lat, lon
            else:
                print(f"[GEOCODING] ✗ No se encontraron resultados para: {direccion_completa}")
        else:
            print(f"[GEOCODING] ✗ Error HTTP {response.status_code}")
        
        # Si falla, intentar solo con localidad y zona
        direccion_fallback = f"{localidad}, {zona}, Argentina"
        params['q'] = direccion_fallback
        
        print(f"[GEOCODING] Reintentando con: {direccion_fallback}")
        time.sleep(1)  # Respetar rate limit de Nominatim
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(f"[GEOCODING] ✓ Encontrado (fallback): lat={lat}, lon={lon}")
                return lat, lon
        
        return None, None
        
    except Exception as e:
        print(f"[GEOCODING] ERROR: {str(e)}")
        return None, None


@login_required(login_url='login_vendedor')
def publicar_repuesto(request):
    """Mostrar formulario para publicar repuesto - requiere login"""
    context = {
        'usuario': request.user,
    }
    return render(request, 'publicar_repuesto.html', context)


@login_required(login_url='login_vendedor')
def procesar_publicacion(request):
    """Procesar publicación de repuesto y buscar solicitudes coincidentes - requiere login"""
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
            
            # Obtener ubicación
            zona = request.POST.get('zona', '')
            localidad = request.POST.get('localidad', '')
            direccion = request.POST.get('direccion', '')
            
            # Construir ubicación completa para compatibilidad
            ubicacion_completa = f"{direccion}, {localidad}, {zona}" if direccion else f"{localidad}, {zona}" if localidad and zona else (localidad or zona or '')
            
            # GEOCODIFICAR LA DIRECCIÓN
            latitud, longitud = geocodificar_direccion(direccion, localidad, zona)
            
            if latitud and longitud:
                print(f"[INFO] Geocodificación exitosa: {latitud}, {longitud}")
            else:
                print(f"[WARN] No se pudo geocodificar la dirección, usando coordenadas aproximadas")
            
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
                zona=zona,
                localidad=localidad,
                direccion=direccion,
                ubicacion=ubicacion_completa,
                latitud=latitud,
                longitud=longitud,
                nombre_vendedor=request.POST.get('nombre_vendedor'),
                email_vendedor=request.POST.get('email_vendedor'),
                telefono_vendedor=request.POST.get('telefono_vendedor')
            )
            
            # Buscar solicitudes que coincidan con este repuesto
            solicitudes_coincidentes = buscar_solicitudes_compatibles(publicacion)
            
            if latitud and longitud:
                messages.success(request, '¡Tu repuesto ha sido publicado exitosamente con ubicación GPS!')
            else:
                messages.warning(request, 'Repuesto publicado, pero no se pudo obtener la ubicación exacta. Se usará la localidad aproximada.')
            
            context = {
                'publicacion': publicacion,
                'solicitudes': solicitudes_coincidentes,
                'total_solicitudes': solicitudes_coincidentes.count(),
                'hay_coincidencias': solicitudes_coincidentes.exists(),
                'usuario': request.user,
            }
            
            return render(request, 'confirmacion_publicacion.html', context)
            
        except Exception as e:
            print(f"[ERROR] Error en procesar_publicacion: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al publicar el repuesto: {str(e)}')
            return redirect('publicar_repuesto')
    
    return redirect('publicar_repuesto')


@login_required(login_url='login_vendedor')
def procesar_venta(request):
    """Alias para procesar_publicacion (mantener compatibilidad) - requiere login"""
    return procesar_publicacion(request)


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
            query = Q(año_auto__gte=publicacion.año_desde, año_auto__lte=publicacion.año_hasta)
        elif publicacion.año_desde:
            query = Q(año_auto__gte=publicacion.año_desde)
        elif publicacion.año_hasta:
            query = Q(año_auto__lte=publicacion.año_hasta)
        
        query |= Q(año_auto__isnull=True)
        solicitudes = solicitudes.filter(query)
    
    return solicitudes.distinct().order_by('-fecha_solicitud')