from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from core.models import SolicitudCompra, PublicacionVenta, VendedorEmpresa, ImagenRepuesto
from decimal import Decimal, InvalidOperation
import json

def quiero_comprar(request):
    """Mostrar formulario de búsqueda de repuestos"""
    return render(request, 'quiero_comprar.html')

def procesar_compra(request):
    """Procesar formulario de búsqueda y mostrar resultados"""
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
                celular=request.POST.get('celular'),
                localidad=request.POST.get('localidad', ''),
                zona=request.POST.get('zona', '')
            )
            
            # ✅ PROCESAR MÚLTIPLES IMÁGENES
            imagenes = request.FILES.getlist('fotos_repuesto')
            for imagen in imagenes:
                ImagenRepuesto.objects.create(
                    solicitud=solicitud,
                    imagen=imagen
                )
            
            print(f"[DEBUG] Solicitud creada con {len(imagenes)} imágenes")
            
            # Obtener vendedores de la zona
            vendedores_ubicaciones = obtener_vendedores_zona(solicitud)
            
            print(f"[DEBUG] Total vendedores encontrados: {len(vendedores_ubicaciones)}")
            
            context = {
                'solicitud': solicitud,
                'total_encontrados': 0,
                'vendedores_json': json.dumps(vendedores_ubicaciones),
                'vendedores_list': vendedores_ubicaciones
            }
            
            return render(request, 'resultados_comprar.html', context)
            
        except Exception as e:
            print(f"[ERROR] Error en procesar_compra: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return redirect('quiero_comprar')
    
    return redirect('quiero_comprar')


def obtener_vendedores_zona(solicitud):
    """
    Obtener TODOS los vendedores con su ubicación GPS
    Prioriza vendedores con coordenadas exactas
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
        
        print(f"[DEBUG] Vendedores encontrados: {vendedores.count()}")
        
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
                print(f"[WARN] ⚠️ {vendedor.nombre_empresa}: Sin coordenadas GPS")
            
            vendedores_ubicaciones.append(vendedor_data)
        
        print(f"[RESUMEN] Total vendedores: {len(vendedores_ubicaciones)}, Con GPS: {sum(1 for v in vendedores_ubicaciones if v.get('tiene_gps'))}")
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