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
        # Si no hay dirección específica, geocodificar solo localidad
        if not direccion or direccion.strip() == '':
            direccion_completa = f"{localidad}, {zona}, Argentina"
        else:
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
        if direccion:  # Solo hacer fallback si había dirección específica
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


# ✅ ELIMINADO @login_required - Ahora cualquiera puede publicar
def publicar_repuesto(request):
    """Mostrar formulario para publicar repuesto - ABIERTO A TODOS"""
    return render(request, 'publicar_repuesto.html')


# ✅ ELIMINADO @login_required - Ahora cualquiera puede publicar
def procesar_publicacion(request):
    """Procesar publicación de repuesto - SIMPLIFICADO (solo datos de contacto)"""
    if request.method == 'POST':
        try:
            print("[DEBUG] ========== INICIO PROCESAMIENTO ==========")
            
            # Obtener ubicación
            zona = request.POST.get('zona', '').strip()
            localidad = request.POST.get('localidad', '').strip()
            direccion = request.POST.get('direccion', '').strip()
            
            # Obtener datos de contacto
            nombre_vendedor = request.POST.get('nombre_vendedor', '').strip()
            email_vendedor = request.POST.get('email_vendedor', '').strip()
            telefono_vendedor = request.POST.get('telefono_vendedor', '').strip()
            
            print(f"[DEBUG] Ubicación: {zona} | {localidad} | {direccion}")
            print(f"[DEBUG] Contacto: {nombre_vendedor} | {email_vendedor} | {telefono_vendedor}")
            
            # Validar campos obligatorios
            if not zona or not localidad:
                messages.error(request, 'Zona y Localidad son obligatorios')
                return redirect('publicar_repuesto')
            
            if not nombre_vendedor or not email_vendedor or not telefono_vendedor:
                messages.error(request, 'Todos los datos de contacto son obligatorios')
                return redirect('publicar_repuesto')
            
            # Construir ubicación completa
            if direccion:
                ubicacion_completa = f"{direccion}, {localidad}, {zona}"
            else:
                ubicacion_completa = f"{localidad}, {zona}"
            
            # GEOCODIFICAR LA DIRECCIÓN
            print(f"[DEBUG] Iniciando geocodificación...")
            latitud, longitud = geocodificar_direccion(direccion, localidad, zona)
            
            if latitud and longitud:
                print(f"[INFO] ✓ Geocodificación exitosa: {latitud}, {longitud}")
            else:
                print(f"[WARN] ✗ No se pudo geocodificar, se guardará sin coordenadas")
            
            # Crear la publicación de venta (SOLO CON DATOS DISPONIBLES)
            publicacion = PublicacionVenta.objects.create(
                # Datos de ubicación
                zona=zona,
                localidad=localidad,
                direccion=direccion if direccion else '',
                ubicacion=ubicacion_completa,
                latitud=latitud,
                longitud=longitud,
                
                # Datos de contacto
                nombre_vendedor=nombre_vendedor,
                email_vendedor=email_vendedor,
                telefono_vendedor=telefono_vendedor,
                
            )
            
            print(f"[DEBUG] ✓ Publicación creada: ID={publicacion.id}")
            
            # Mensaje de éxito
            if latitud and longitud:
                messages.success(request, '¡Tu contacto ha sido registrado exitosamente con ubicación GPS! 🎉')
            else:
                messages.success(request, '¡Tu contacto ha sido registrado exitosamente! 📍')
            
            # Contexto para la confirmación
            context = {
                'publicacion': publicacion,
                'total_solicitudes': 0,
                'hay_coincidencias': False,
            }
            
            print("[DEBUG] ========== FIN PROCESAMIENTO ==========")
            
            return render(request, 'confirmacion_publicacion.html', context)
            
        except Exception as e:
            print(f"[ERROR] ========== ERROR EN PROCESAMIENTO ==========")
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            print("[ERROR] ========================================")
            
            messages.error(request, f'Error al registrar: {str(e)}')
            return redirect('publicar_repuesto')
    
    # Si no es POST, redirigir al formulario
    print("[DEBUG] Redirigiendo a formulario (método no es POST)")
    return redirect('publicar_repuesto')


# ✅ ELIMINADO @login_required
def procesar_venta(request):
    """Alias para procesar_publicacion (mantener compatibilidad)"""
    return procesar_publicacion(request)


def buscar_solicitudes_compatibles(publicacion):
    """
    Buscar solicitudes de compra que coincidan con un repuesto publicado
    """
    solicitudes = SolicitudCompra.objects.filter(activa=True)
    
    # 1. FILTRO POR CATEGORÍA (debe coincidir)
    if publicacion.categoria:
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