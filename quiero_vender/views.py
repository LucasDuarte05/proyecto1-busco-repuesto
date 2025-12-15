from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from core.models import SolicitudCompra, PublicacionVenta, VendedorEmpresa, Cotizacion
from django.db.models import Q, Count, Exists, OuterRef
import requests
import time
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


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
    """Ver todas las solicitudes de compra activas - requiere login y perfil completo"""
    
    # ✅ SI ES SUPERUSER, PERMITIR ACCESO SIN VERIFICAR PERFIL
    if request.user.is_superuser:
        # Para admin, mostrar todas las solicitudes sin filtro de vendedor
        solicitudes = SolicitudCompra.objects.filter(activa=True).annotate(
            total_cotizaciones=Count('cotizaciones'),
            tiene_mi_cotizacion=Exists(
                Cotizacion.objects.filter(solicitud=OuterRef('pk'))
            ),
            tiene_cliente_interesado=Exists(
                Cotizacion.objects.filter(
                    solicitud=OuterRef('pk'),
                    estado='cliente_interesado'
                )
            )
        ).order_by('-fecha_solicitud')
        
        # Admin ve todas las solicitudes sin cotización propia
        solicitudes_con_cotizacion = []
        for solicitud in solicitudes:
            solicitudes_con_cotizacion.append({
                'solicitud': solicitud,
                'mi_cotizacion': None  # Admin no cotiza
            })
        
        context = {
            'solicitudes_con_cotizacion': solicitudes_con_cotizacion,
            'total_solicitudes': solicitudes.count(),
            'marcas_disponibles': SolicitudCompra.objects.filter(activa=True).values_list('marca_auto', flat=True).distinct().order_by('marca_auto'),
            'categorias_disponibles': SolicitudCompra.CATEGORIA_CHOICES,
            'urgencias_disponibles': SolicitudCompra.URGENCIA_CHOICES,
            'usuario': request.user,
            'vendedor': None,  # Admin no tiene vendedor
        }
        
        return render(request, 'listado_solicitudes.html', context)
    
    # ✅ PARA USUARIOS NORMALES, VERIFICAR PERFIL COMPLETO
    if not verificar_perfil_completo(request.user):
        return redirect('completar_perfil')
    
    vendedor = request.user.vendedor_empresa
    
    # ... resto del código original ...
    solicitudes = SolicitudCompra.objects.filter(activa=True).annotate(
        total_cotizaciones=Count('cotizaciones'),
        tiene_mi_cotizacion=Exists(
            Cotizacion.objects.filter(
                solicitud=OuterRef('pk'),
                vendedor=vendedor
            )
        ),
        tiene_cliente_interesado=Exists(
            Cotizacion.objects.filter(
                solicitud=OuterRef('pk'),
                estado='cliente_interesado'
            )
        )
    )
    
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
    
    # Obtener cotización del vendedor para cada solicitud (si existe)
    solicitudes_con_cotizacion = []
    for solicitud in solicitudes:
        try:
            mi_cotizacion = Cotizacion.objects.get(
                solicitud=solicitud,
                vendedor=vendedor
            )
        except Cotizacion.DoesNotExist:
            mi_cotizacion = None
        
        solicitudes_con_cotizacion.append({
            'solicitud': solicitud,
            'mi_cotizacion': mi_cotizacion
        })
    
    # Obtener valores únicos para los filtros
    marcas_disponibles = SolicitudCompra.objects.filter(activa=True).values_list('marca_auto', flat=True).distinct().order_by('marca_auto')
    categorias_disponibles = SolicitudCompra.CATEGORIA_CHOICES
    urgencias_disponibles = SolicitudCompra.URGENCIA_CHOICES
    
    context = {
        'solicitudes_con_cotizacion': solicitudes_con_cotizacion,
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
        'vendedor': vendedor,
    }
    
    return render(request, 'listado_solicitudes.html', context)


@login_required(login_url='login_vendedor')
def enviar_cotizacion(request, solicitud_id):
    """Enviar o actualizar cotización para una solicitud"""
    if request.method != 'POST':
        return redirect('ver_solicitudes')
    
    # Verificar perfil
    if not verificar_perfil_completo(request.user):
        return redirect('completar_perfil')
    
    vendedor = request.user.vendedor_empresa
    solicitud = get_object_or_404(SolicitudCompra, id=solicitud_id, activa=True)
    
    try:
        precio = Decimal(request.POST.get('precio', '0'))
        comentarios = request.POST.get('comentarios', '').strip()
        
        # Validar precio
        if precio <= 0:
            messages.error(request, 'El precio debe ser mayor a 0')
            return redirect('ver_solicitudes')
        
        # Buscar si ya existe una cotización
        cotizacion, created = Cotizacion.objects.get_or_create(
            solicitud=solicitud,
            vendedor=vendedor,
            defaults={
                'precio': precio,
                'comentarios': comentarios,
                'estado': 'pendiente'
            }
        )
        
        if not created:
            # Si ya existe y está pendiente, permitir actualización
            if cotizacion.estado == 'pendiente':
                cotizacion.precio = precio
                cotizacion.comentarios = comentarios
                cotizacion.save()
                messages.success(request, '✅ Cotización actualizada exitosamente')
            else:
                messages.warning(request, f'Ya tienes una cotización {cotizacion.get_estado_display()} para esta solicitud')
        else:
            messages.success(request, '✅ Cotización enviada exitosamente. Está pendiente de aprobación.')
        
    except Exception as e:
        messages.error(request, f'Error al enviar cotización: {str(e)}')
    
    return redirect('ver_solicitudes')


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


def publicar_repuesto(request):
    """Mostrar formulario para publicar repuesto - ABIERTO A TODOS"""
    return render(request, 'publicar_repuesto.html')


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


@login_required(login_url='login_vendedor')
def completar_perfil(request):
    """Mostrar formulario para completar perfil de vendedor"""
    # Si ya tiene perfil, redirigir a solicitudes
    try:
        vendedor = request.user.vendedor_empresa
        return redirect('ver_solicitudes')
    except VendedorEmpresa.DoesNotExist:
        pass
    
    return render(request, 'completar_perfil.html')


@login_required(login_url='login_vendedor')
def guardar_perfil(request):
    """Guardar perfil de vendedor con geocodificación"""
    if request.method == 'POST':
        try:
            # Verificar si ya tiene perfil
            if hasattr(request.user, 'vendedor_empresa'):
                messages.warning(request, 'Ya tienes un perfil registrado')
                return redirect('ver_solicitudes')
            
            # Validar CUIT único
            cuit = request.POST.get('cuit', '').strip()
            if VendedorEmpresa.objects.filter(cuit=cuit).exists():
                messages.error(request, 'Este CUIT ya está registrado')
                return render(request, 'completar_perfil.html', {'error': 'Este CUIT ya está registrado'})
            
            # Obtener datos de ubicación
            direccion = request.POST.get('direccion', '').strip()
            localidad = request.POST.get('localidad', '').strip()
            provincia = request.POST.get('provincia', '').strip()
            
            # 🌍 GEOCODIFICAR LA DIRECCIÓN
            print(f"[VENDEDOR] Geocodificando: {direccion}, {localidad}, {provincia}")
            latitud, longitud = geocodificar_direccion(direccion, localidad, provincia)
            
            if latitud and longitud:
                print(f"[VENDEDOR] ✅ Coordenadas obtenidas: {latitud}, {longitud}")
            else:
                print(f"[VENDEDOR] ⚠️ No se pudo geocodificar")
            
            # Crear perfil de vendedor
            vendedor = VendedorEmpresa.objects.create(
                user=request.user,
                nombre_empresa=request.POST.get('nombre_empresa', '').strip(),
                cuit=cuit,
                telefono=request.POST.get('telefono', '').strip(),
                direccion=direccion,
                localidad=localidad,
                provincia=provincia,
                web_ig=request.POST.get('web_ig', '').strip(),
                latitud=latitud,
                longitud=longitud
            )
            
            if latitud and longitud:
                messages.success(request, '¡Perfil completado exitosamente con ubicación GPS! 📍 Ya puedes cotizar repuestos.')
            else:
                messages.success(request, '¡Perfil completado! Ya puedes cotizar repuestos.')
            
            return redirect('ver_solicitudes')
            
        except Exception as e:
            print(f"[ERROR] Error al guardar perfil: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al guardar el perfil: {str(e)}')
            return render(request, 'completar_perfil.html', {'error': str(e)})
    
    return redirect('completar_perfil')


def verificar_perfil_completo(user):
    """Verificar si el usuario tiene perfil de vendedor completo"""
    try:
        vendedor = user.vendedor_empresa
        return True
    except VendedorEmpresa.DoesNotExist:
        return False



@login_required(login_url='admin_login')  # ✅ Cambio: login_url apunta a admin_login
def admin_cotizaciones(request):
    """Panel principal de administración de cotizaciones"""
    
    # Verificar si es superuser
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('admin_login')
    
    # Obtener filtros
    estado_filtro = request.GET.get('estado', 'pendiente')
    
    # Obtener cotizaciones
    cotizaciones = Cotizacion.objects.select_related(
        'solicitud', 'vendedor', 'vendedor__user'
    ).all()
    
    # Aplicar filtro de estado
    if estado_filtro and estado_filtro != 'todas':
        cotizaciones = cotizaciones.filter(estado=estado_filtro)
    
    cotizaciones = cotizaciones.order_by('-fecha_creacion')
    
    # Contadores por estado
    contadores = {
        'total': Cotizacion.objects.count(),
        'pendiente': Cotizacion.objects.filter(estado='pendiente').count(),
        'enviada': Cotizacion.objects.filter(estado='enviada').count(),
        'rechazada': Cotizacion.objects.filter(estado='rechazada').count(),
        'cliente_interesado': Cotizacion.objects.filter(estado='cliente_interesado').count(),
    }
    
    context = {
        'cotizaciones': cotizaciones,
        'contadores': contadores,
        'estado_actual': estado_filtro,
        'estados_choices': Cotizacion.ESTADOS,
    }
    
    return render(request, 'admin_cotizaciones.html', context)


@staff_member_required
def detalle_cotizacion(request, cotizacion_id):
    """Vista detallada de una cotización con opciones de aprobar/rechazar"""
    
    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related('solicitud', 'vendedor', 'vendedor__user'),
        id=cotizacion_id
    )
    
    # Procesar acciones
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'aprobar':
            cotizacion.estado = 'enviada'
            cotizacion.fecha_envio = timezone.now()
            cotizacion.save()
            
            # ✅ ENVIAR EMAIL AL CLIENTE
            try:
                enviar_email_cotizacion(cotizacion, request)
                messages.success(request, '✅ Cotización aprobada y email enviado al cliente')
            except Exception as e:
                messages.warning(request, f'⚠️ Cotización aprobada pero hubo un error al enviar el email: {str(e)}')
            
        elif accion == 'rechazar':
            cotizacion.estado = 'rechazada'
            cotizacion.save()
            messages.warning(request, '❌ Cotización rechazada')
        
        return redirect('detalle_cotizacion', cotizacion_id=cotizacion.id)
    
    context = {
        'cotizacion': cotizacion,
        'solicitud': cotizacion.solicitud,
        'vendedor': cotizacion.vendedor,
    }
    
    return render(request, 'detalle_cotizacion.html', context)


@staff_member_required
def perfil_vendedor_admin(request, vendedor_id):
    """Perfil del vendedor con historial de cotizaciones"""
    
    vendedor = get_object_or_404(VendedorEmpresa, id=vendedor_id)
    
    # Obtener todas las cotizaciones del vendedor
    cotizaciones = Cotizacion.objects.filter(
        vendedor=vendedor
    ).select_related('solicitud').order_by('-fecha_creacion')
    
    # Estadísticas
    estadisticas = {
        'total_cotizaciones': cotizaciones.count(),
        'aprobadas': cotizaciones.filter(estado='enviada').count(),
        'rechazadas': cotizaciones.filter(estado='rechazada').count(),
        'pendientes': cotizaciones.filter(estado='pendiente').count(),
        'con_interes': cotizaciones.filter(estado='cliente_interesado').count(),
    }
    
    context = {
        'vendedor': vendedor,
        'cotizaciones': cotizaciones,
        'estadisticas': estadisticas,
    }
    
    return render(request, 'perfil_vendedor_admin.html', context)

def admin_login(request):
    """Página de login para administradores (SIN requerir estar autenticado)"""
    # Si ya está autenticado y es superuser, ir al panel
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_cotizaciones')
    
    return render(request, 'admin_login.html')


def admin_verificar(request):
    """Verificar credenciales de superuser y dar acceso al panel"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            # Usuario es superuser, autenticar y dar acceso
            login(request, user)  # ✅ Agregar esta línea
            messages.success(request, '✅ Acceso concedido al panel de administración')
            return redirect('admin_cotizaciones')
        else:
            # Credenciales inválidas o no es superuser
            messages.error(request, '❌ Usuario o contraseña incorrectos, o no tienes permisos de administrador')
            return redirect('admin_login')
    
    return redirect('admin_login')


def enviar_email_cotizacion(cotizacion, request):
    """
    Enviar email al cliente cuando se aprueba una cotización
    """
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from django.urls import reverse
    
    solicitud = cotizacion.solicitud
    vendedor = cotizacion.vendedor
    
    # Construir URLs absolutas
    url_interes = request.build_absolute_uri(
        reverse('cliente_interes', args=[cotizacion.id])
    )
    
    # WhatsApp con mensaje pre-escrito
    mensaje_wa = f"Hola! Vi tu cotización de ${cotizacion.precio} para {solicitud.repuesto_especifico}. Me interesa!"
    telefono_wa = vendedor.telefono.replace('-', '').replace(' ', '')
    url_whatsapp = f"https://wa.me/549{telefono_wa}?text={mensaje_wa}"
    
    # Contexto para los templates
    context = {
        'cotizacion': cotizacion,
        'solicitud': solicitud,
        'vendedor': vendedor,
        'url_interes': url_interes,
        'url_whatsapp': url_whatsapp,
    }
    
    # Renderizar templates
    html_content = render_to_string('emails/cotizacion_aprobada.html', context)
    text_content = render_to_string('emails/cotizacion_aprobada.txt', context)
    
    # Crear email
    subject = f'💰 Nueva cotización para {solicitud.repuesto_especifico} - Busco Repuesto'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = solicitud.celular  # Usar celular si no hay email
    
    # Si la solicitud tiene email, usarlo
    if hasattr(solicitud, 'email') and solicitud.email:
        to_email = solicitud.email
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email]
    )
    
    # Adjuntar versión HTML
    email.attach_alternative(html_content, "text/html")
    
    # Enviar
    email.send(fail_silently=False)
    
    print(f"[EMAIL] ✓ Email enviado a {to_email}")
    return True


def cliente_interes(request, cotizacion_id):
    """
    Vista pública: el cliente muestra interés en una cotización
    """
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    
    # Verificar que la cotización esté enviada
    if cotizacion.estado != 'enviada':
        messages.warning(request, 'Esta cotización ya no está disponible')
        return redirect('index')
    
    # Cambiar estado a "cliente_interesado"
    cotizacion.estado = 'cliente_interesado'
    cotizacion.save()
    
    # Enviar notificación al vendedor
    try:
        enviar_email_vendedor_interes(cotizacion, request)
        messages.success(request, '✅ ¡Perfecto! El vendedor recibirá tus datos de contacto.')
    except Exception as e:
        print(f"[ERROR] No se pudo enviar email al vendedor: {str(e)}")
        messages.warning(request, '⚠️ Registramos tu interés, pero hubo un error al notificar al vendedor.')
    
    context = {
        'cotizacion': cotizacion,
        'solicitud': cotizacion.solicitud,
        'vendedor': cotizacion.vendedor,
    }
    
    return render(request, 'cliente_interesado.html', context)


def enviar_email_vendedor_interes(cotizacion, request):
    """
    Notificar al vendedor que el cliente está interesado
    """
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    
    solicitud = cotizacion.solicitud
    vendedor = cotizacion.vendedor
    
    # WhatsApp al cliente
    mensaje_wa = f"Hola {solicitud.nombre}! Soy de {vendedor.nombre_empresa}. Me contacto por tu interés en el {solicitud.repuesto_especifico}."
    telefono_cliente = solicitud.celular.replace('-', '').replace(' ', '')
    url_whatsapp = f"https://wa.me/549{telefono_cliente}?text={mensaje_wa}"
    
    context = {
        'cotizacion': cotizacion,
        'solicitud': solicitud,
        'vendedor': vendedor,
        'url_whatsapp': url_whatsapp,
    }
    
    # Renderizar templates
    html_content = render_to_string('emails/vendedor_cliente_interesado.html', context)
    text_content = render_to_string('emails/vendedor_cliente_interesado.txt', context)
    
    # Email del vendedor (usar el email del user de Django)
    to_email = vendedor.user.email
    
    subject = f'🎉 Cliente interesado en tu cotización - {solicitud.repuesto_especifico}'
    from_email = settings.DEFAULT_FROM_EMAIL
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email]
    )
    
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
    
    print(f"[EMAIL] ✓ Email de interés enviado a vendedor: {to_email}")
    return True