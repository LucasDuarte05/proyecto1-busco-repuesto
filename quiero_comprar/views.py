from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from core.models import SolicitudCompra, PublicacionVenta, VendedorEmpresa, ImagenRepuesto
from decimal import Decimal, InvalidOperation
import json

def quiero_comprar(request):
    """Mostrar formulario de búsqueda de repuestos"""
    return render(request, 'quiero_comprar/quiero_comprar.html')

def procesar_compra(request):
    """Procesar formulario de búsqueda y mostrar resultados con mapa"""
    print(f"[DEBUG] Método recibido: {request.method}")
    print(f"[DEBUG] POST data: {request.POST}")
    
    if request.method == 'POST':
        try:
            # Obtener y validar datos
            marca_auto = request.POST.get('marca_auto')
            repuesto_especifico = request.POST.get('repuesto_especifico')
            nombre = request.POST.get('nombre')
            celular = request.POST.get('celular')
            
            print(f"[DEBUG] Datos recibidos - Marca: {marca_auto}, Repuesto: {repuesto_especifico}")
            
            # Validar campos obligatorios
            if not all([marca_auto, repuesto_especifico, nombre, celular]):
                print("[ERROR] Faltan campos obligatorios")
                messages.error(request, 'Por favor completa todos los campos obligatorios')
                return redirect('quiero_comprar')
            
            # Crear la solicitud de compra
            solicitud = SolicitudCompra.objects.create(
                marca_auto=marca_auto,
                modelo_auto=request.POST.get('modelo_auto', ''),
                año_auto=request.POST.get('año_auto') if request.POST.get('año_auto') else None,
                nro_chasis=request.POST.get('nro_chasis', ''),
                categoria_repuesto=request.POST.get('categoria_repuesto'),
                repuesto_especifico=repuesto_especifico,
                descripcion_adicional=request.POST.get('descripcion_adicional', ''),
                urgencia=request.POST.get('urgencia'),
                nombre=nombre,
                celular=celular,
                localidad=request.POST.get('localidad', ''),
                zona=request.POST.get('zona', '')
            )
            
            print(f"[DEBUG] ✅ Solicitud creada con ID: {solicitud.id}")
            
            # Procesar múltiples imágenes
            imagenes = request.FILES.getlist('fotos_repuesto')
            for imagen in imagenes:
                ImagenRepuesto.objects.create(
                    solicitud=solicitud,
                    imagen=imagen
                )
            
            print(f"[DEBUG] Imágenes procesadas: {len(imagenes)}")
            
            # Obtener vendedores de la zona con sus coordenadas GPS
            vendedores_ubicaciones = obtener_vendedores_zona(solicitud)
            
            print(f"[DEBUG] Vendedores encontrados: {len(vendedores_ubicaciones)}")
            
            # Contar vendedores con GPS
            vendedores_con_gps = sum(1 for v in vendedores_ubicaciones if v.get('tiene_gps'))
            
            context = {
                'solicitud': solicitud,
                'total_encontrados': len(vendedores_ubicaciones),
                'vendedores_con_gps': vendedores_con_gps,
                'vendedores_json': json.dumps(vendedores_ubicaciones),
                'vendedores_list': vendedores_ubicaciones
            }
            
            print(f"[DEBUG] ✅ Renderizando resultados_comprar.html")
            print(f"[DEBUG] Context: total={context['total_encontrados']}, con_gps={context['vendedores_con_gps']}")
            
            messages.success(request, f'✅ Solicitud enviada exitosamente. Encontramos {len(vendedores_ubicaciones)} vendedor{"es" if len(vendedores_ubicaciones) != 1 else ""} en tu zona.')
            
            # IMPORTANTE: render directo, NO redirect
            return render(request, 'resultados_comprar.html', context)
            
        except Exception as e:
            print(f"[ERROR] ❌ Error en procesar_compra: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return redirect('quiero_comprar')
    
    # Si no es POST, redirigir al formulario
    print("[DEBUG] No es POST, redirigiendo a quiero_comprar")
    return redirect('quiero_comprar')

def obtener_vendedores_zona(solicitud):
    """
    Obtener vendedores activos con ubicación GPS prioritaria
    """
    vendedores_ubicaciones = []
    
    try:
        # Obtener TODOS los vendedores activos
        vendedores = VendedorEmpresa.objects.filter(activo=True)
        
        # Filtrar por zona/provincia si están disponibles
        if solicitud.zona or solicitud.localidad:
            query_geo = Q()
            if solicitud.zona:
                query_geo |= Q(provincia__icontains=solicitud.zona)
            if solicitud.localidad:
                query_geo |= Q(localidad__icontains=solicitud.localidad)
            
            vendedores = vendedores.filter(query_geo)
        
        print(f"[DEBUG] Vendedores encontrados en la zona: {vendedores.count()}")
        
        # Crear lista de vendedores con coordenadas
        for vendedor in vendedores:
            vendedor_data = {
                'nombre': vendedor.nombre_empresa,
                'email': vendedor.user.email,
                'telefono': vendedor.telefono,
                'zona': vendedor.provincia,
                'localidad': vendedor.localidad,
                'direccion': vendedor.direccion,
            }
            
            # 🎯 PRIORIDAD: Usar coordenadas GPS si existen
            if vendedor.latitud and vendedor.longitud:
                vendedor_data['latitud'] = float(vendedor.latitud)
                vendedor_data['longitud'] = float(vendedor.longitud)
                vendedor_data['tiene_gps'] = True
                print(f"[GPS] ✅ {vendedor.nombre_empresa}: {vendedor_data['latitud']}, {vendedor_data['longitud']}")
            else:
                vendedor_data['tiene_gps'] = False
                print(f"[WARN] ⚠️ {vendedor.nombre_empresa}: Sin coordenadas GPS guardadas")
            
            vendedores_ubicaciones.append(vendedor_data)
        
        print(f"[RESUMEN] Total: {len(vendedores_ubicaciones)} | Con GPS: {sum(1 for v in vendedores_ubicaciones if v.get('tiene_gps'))}")
        return vendedores_ubicaciones
        
    except Exception as e:
        print(f"[ERROR] Error en obtener_vendedores_zona: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def listado_repuestos(request):
    """Mostrar todos los repuestos disponibles"""
    try:
        # Obtener todas las publicaciones disponibles
        repuestos = PublicacionVenta.objects.filter(disponible=True)
        
        context = {
            'repuestos': repuestos,
            'total_repuestos': repuestos.count()
        }
        return render(request, 'listado_repuestos.html', context)
        
    except Exception as e:
        print(f"[ERROR] Error al cargar repuestos: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error al cargar los repuestos: {str(e)}')
        context = {
            'repuestos': [],
            'total_repuestos': 0
        }
        return render(request, 'listado_repuestos.html', context)


def procesar_solicitud(request):
    """Procesar solicitud de repuesto y mostrar confirmación"""
    if request.method == 'POST':
        try:
            # Crear la solicitud de compra
            solicitud = SolicitudCompra.objects.create(
                marca_auto=request.POST.get('marca_auto'),
                modelo_auto=request.POST.get('modelo_auto', ''),
                año_auto=request.POST.get('año_auto') if request.POST.get('año_auto') else None,
                nro_chasis=request.POST.get('nro_chasis', ''),
                categoria_repuesto=request.POST.get('categoria_repuesto'),
                repuesto_especifico=request.POST.get('repuesto_especifico'),
                descripcion_adicional=request.POST.get('descripcion_adicional', ''),
                urgencia=request.POST.get('urgencia'),
                nombre=request.POST.get('nombre'),
                email=request.POST.get('email'),
                celular=request.POST.get('celular'),
                localidad=request.POST.get('localidad', ''),
                zona=request.POST.get('zona', '')
            )
            
            messages.success(request, '¡Tu solicitud ha sido registrada exitosamente!')
            
            context = {
                'solicitud': solicitud,
                'total_encontrados': 0,
                'hay_coincidencias': False
            }
            
            return render(request, 'confirmacion_solicitud.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return redirect('quiero_comprar')

    return redirect('quiero_comprar')
