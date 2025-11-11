from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from core.models import SolicitudCompra, PublicacionVenta
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
                email=request.POST.get('email'),
                celular=request.POST.get('celular'),
                localidad=request.POST.get('localidad', ''),
                zona=request.POST.get('zona', '')
            )
            
            # Buscar repuestos con algoritmo de coincidencia mejorado
            repuestos_disponibles = buscar_repuestos_compatibles(solicitud)
            
            # Obtener vendedores únicos con sus ubicaciones COMPLETAS y COORDENADAS GPS
            # SIEMPRE mostrar vendedores de la zona, aunque no tengan el repuesto exacto
            vendedores_ubicaciones = obtener_vendedores_zona(solicitud, repuestos_disponibles)
            
            print(f"[DEBUG] Total vendedores encontrados: {len(vendedores_ubicaciones)}")
            
            context = {
                'solicitud': solicitud,
                'repuestos': repuestos_disponibles,
                'total_encontrados': len(repuestos_disponibles),
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


def obtener_vendedores_zona(solicitud, repuestos_disponibles):
    """
    Obtener vendedores de la zona del usuario
    Prioriza vendedores con repuestos coincidentes, pero muestra TODOS los vendedores cercanos
    """
    vendedores_ubicaciones = []
    vendedores_vistos = set()
    
    # 1. PRIMERO: Agregar vendedores que tienen repuestos coincidentes
    for repuesto in repuestos_disponibles:
        vendedor_key = f"{repuesto.email_vendedor}_{repuesto.zona}_{repuesto.localidad}_{repuesto.direccion}"
        
        if vendedor_key not in vendedores_vistos:
            vendedores_vistos.add(vendedor_key)
            
            repuestos_count = sum(
                1 for r in repuestos_disponibles 
                if r.email_vendedor == repuesto.email_vendedor 
                and r.zona == repuesto.zona 
                and r.localidad == repuesto.localidad
                and r.direccion == repuesto.direccion
            )
            
            vendedor_data = {
                'nombre': repuesto.nombre_vendedor,
                'email': repuesto.email_vendedor,
                'telefono': repuesto.telefono_vendedor,
                'zona': repuesto.zona,
                'localidad': repuesto.localidad,
                'direccion': repuesto.direccion if repuesto.direccion else '',
                'repuestos_count': repuestos_count,
                'tiene_repuesto_exacto': True
            }
            
            # ✅ FIX CRÍTICO: Convertir Decimal a float
            if repuesto.latitud and repuesto.longitud:
                vendedor_data['latitud'] = float(repuesto.latitud)
                vendedor_data['longitud'] = float(repuesto.longitud)
                vendedor_data['tiene_gps'] = True
                print(f"[GPS] ✓ {repuesto.nombre_vendedor}: {vendedor_data['latitud']}, {vendedor_data['longitud']}")
            else:
                vendedor_data['tiene_gps'] = False
            
            vendedores_ubicaciones.append(vendedor_data)
    
    # 2. SEGUNDO: Agregar vendedores de la MISMA ZONA
    if solicitud.zona or solicitud.localidad:
        try:
            repuestos_zona = PublicacionVenta.objects.filter(
                disponible=True
            ).exclude(
                precio__isnull=True
            ).extra(
                where=["precio != ''"]
            )
            
            if solicitud.zona and solicitud.localidad:
                repuestos_zona = repuestos_zona.filter(
                    Q(zona__icontains=solicitud.zona) | Q(localidad__icontains=solicitud.localidad)
                )
            elif solicitud.zona:
                repuestos_zona = repuestos_zona.filter(zona__icontains=solicitud.zona)
            elif solicitud.localidad:
                repuestos_zona = repuestos_zona.filter(localidad__icontains=solicitud.localidad)
            
            repuestos_zona = repuestos_zona.distinct()
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            repuestos_zona = PublicacionVenta.objects.none()
        
        for repuesto in repuestos_zona:
            vendedor_key = f"{repuesto.email_vendedor}_{repuesto.zona}_{repuesto.localidad}_{repuesto.direccion}"
            
            if vendedor_key not in vendedores_vistos:
                vendedores_vistos.add(vendedor_key)
                
                repuestos_count = PublicacionVenta.objects.filter(
                    email_vendedor=repuesto.email_vendedor,
                    zona=repuesto.zona,
                    localidad=repuesto.localidad,
                    direccion=repuesto.direccion,
                    disponible=True
                ).exclude(
                    precio__isnull=True
                ).extra(
                    where=["precio != ''"]
                ).count()
                
                vendedor_data = {
                    'nombre': repuesto.nombre_vendedor,
                    'email': repuesto.email_vendedor,
                    'telefono': repuesto.telefono_vendedor,
                    'zona': repuesto.zona,
                    'localidad': repuesto.localidad,
                    'direccion': repuesto.direccion if repuesto.direccion else '',
                    'repuestos_count': repuestos_count,
                    'tiene_repuesto_exacto': False
                }
                
                # ✅ FIX CRÍTICO: Convertir Decimal a float
                if repuesto.latitud and repuesto.longitud:
                    vendedor_data['latitud'] = float(repuesto.latitud)
                    vendedor_data['longitud'] = float(repuesto.longitud)
                    vendedor_data['tiene_gps'] = True
                    print(f"[GPS] ✓ {repuesto.nombre_vendedor}: {vendedor_data['latitud']}, {vendedor_data['longitud']}")
                else:
                    vendedor_data['tiene_gps'] = False
                
                vendedores_ubicaciones.append(vendedor_data)
    
    print(f"[RESUMEN] Vendedores: {len(vendedores_ubicaciones)}, Con GPS: {sum(1 for v in vendedores_ubicaciones if v.get('tiene_gps'))}")
    return vendedores_ubicaciones


def listado_repuestos(request):
    """Mostrar todos los repuestos disponibles"""
    try:
        # ✅ Usar extra() para filtrar precios vacíos correctamente
        repuestos = PublicacionVenta.objects.filter(
            disponible=True
        ).exclude(
            precio__isnull=True
        ).extra(
            where=["precio != ''"]
        )
        
        # Convertir a lista y validar manualmente por seguridad adicional
        repuestos_validos = []
        for repuesto in repuestos.iterator():
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
    """Procesar solicitud de repuesto y mostrar confirmación con coincidencias"""
    if request.method == 'POST':
        try:
            # Crear la solicitud de compra con los campos correctos del modelo
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
            
            # Buscar repuestos que coincidan con la solicitud
            repuestos_disponibles = buscar_repuestos_compatibles(solicitud)
            
            messages.success(request, '¡Tu solicitud ha sido registrada exitosamente!')
            
            # Contexto común
            context = {
                'solicitud': solicitud,
                'repuestos': repuestos_disponibles,
                'total_encontrados': len(repuestos_disponibles),
                'hay_coincidencias': len(repuestos_disponibles) > 0
            }
            
            return render(request, 'confirmacion_solicitud.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return redirect('quiero_comprar')

    return redirect('quiero_comprar')

def listado_repuestos(request):
    """Mostrar todos los repuestos disponibles"""
    try:
        # Obtener todos los repuestos disponibles CON PRECIOS VÁLIDOS
        repuestos = PublicacionVenta.objects.filter(
            disponible=True
        ).exclude(
            precio__isnull=True
        ).exclude(
            precio=''
        )
        
        # Convertir a lista y validar manualmente por seguridad adicional
        repuestos_validos = []
        for repuesto in repuestos.iterator():
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


def buscar_repuestos_compatibles(solicitud):
    """
    Algoritmo de búsqueda MEJORADO con filtros más flexibles
    Prioriza coincidencias pero no descarta repuestos compatibles
    """
    try:
        # 1. COMENZAR CON TODOS LOS REPUESTOS DISPONIBLES (CON PRECIOS VÁLIDOS)
        # Usar .extra() para filtrar cadenas vacías en SQLite
        repuestos = PublicacionVenta.objects.filter(
            disponible=True
        ).exclude(
            precio__isnull=True
        ).extra(
            where=["precio != ''"]
        )
        
        print(f"[DEBUG] Total repuestos disponibles: {repuestos.count()}")
        
        # 2. FILTRO POR CATEGORÍA (intentar, pero si no hay resultados, relajar)
        repuestos_categoria = repuestos.filter(categoria=solicitud.categoria_repuesto)
        print(f"[DEBUG] Después de filtrar por categoría '{solicitud.categoria_repuesto}': {repuestos_categoria.count()}")
        
        # Si hay repuestos en la categoría, usarlos; sino, usar todos
        if repuestos_categoria.exists():
            repuestos = repuestos_categoria
        else:
            print(f"[DEBUG] No hay repuestos en categoría '{solicitud.categoria_repuesto}', buscando en todas las categorías")
        
        # 3. FILTRO GEOGRÁFICO (PRIORIZAR ZONA/LOCALIDAD)
        repuestos_geograficos = None
        if solicitud.zona or solicitud.localidad:
            query_geo = Q()
            if solicitud.zona:
                query_geo |= Q(zona__icontains=solicitud.zona)
            if solicitud.localidad:
                query_geo |= Q(localidad__icontains=solicitud.localidad)
            
            repuestos_geograficos = repuestos.filter(query_geo)
            
            # Si hay resultados cercanos, priorizarlos
            if repuestos_geograficos.exists():
                print(f"[DEBUG] Repuestos en zona '{solicitud.zona}'/'{solicitud.localidad}': {repuestos_geograficos.count()}")
                # Ordenar: primero los de la zona, luego los demás
                repuestos_lejanos = repuestos.exclude(query_geo)
                repuestos = list(repuestos_geograficos) + list(repuestos_lejanos)
            else:
                print(f"[DEBUG] No hay repuestos en la zona, mostrando todos")
                repuestos = list(repuestos)
        else:
            repuestos = list(repuestos)
        
        # Convertir a queryset si es lista
        if isinstance(repuestos, list):
            if len(repuestos) == 0:
                print(f"[DEBUG] Lista de repuestos vacía después de filtros geográficos")
                return []
            repuestos_ids = [r.id for r in repuestos]
            repuestos = PublicacionVenta.objects.filter(
                id__in=repuestos_ids, 
                disponible=True
            ).exclude(precio__isnull=True).exclude(precio='')
        
        # 4. FILTRO FLEXIBLE POR MARCA (opcional)
        if solicitud.marca_auto:
            repuestos_marca = repuestos.filter(
                Q(marca_auto__iexact=solicitud.marca_auto) |
                Q(marca_auto__icontains=solicitud.marca_auto) |
                Q(marca_auto__icontains='Universal') |
                Q(marca_auto__icontains='Todos') |
                Q(marca_auto='')
            )
            
            if repuestos_marca.exists():
                repuestos = repuestos_marca
                print(f"[DEBUG] Después de filtrar por marca '{solicitud.marca_auto}': {repuestos.count()}")
            else:
                print(f"[DEBUG] No hay repuestos para marca '{solicitud.marca_auto}', manteniendo resultados previos")
        
        # 5. FILTRO OPCIONAL POR MODELO
        if solicitud.modelo_auto:
            repuestos_modelo = repuestos.filter(
                Q(modelo_auto__icontains=solicitud.modelo_auto) |
                Q(modelo_auto='') |
                Q(modelo_auto__isnull=True)
            )
            
            if repuestos_modelo.exists():
                repuestos = repuestos_modelo
                print(f"[DEBUG] Después de filtrar por modelo '{solicitud.modelo_auto}': {repuestos.count()}")
        
        # 6. FILTRO FLEXIBLE POR AÑO
        if solicitud.año_auto:
            año = solicitud.año_auto
            repuestos_año = repuestos.filter(
                Q(
                    (Q(año_desde__lte=año) | Q(año_desde__isnull=True)) &
                    (Q(año_hasta__gte=año) | Q(año_hasta__isnull=True))
                ) |
                Q(año_desde__isnull=True, año_hasta__isnull=True)
            )
            
            if repuestos_año.exists():
                repuestos = repuestos_año
                print(f"[DEBUG] Después de filtrar por año {año}: {repuestos.count()}")
        
        # 7. BÚSQUEDA FLEXIBLE POR TÍTULO
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
        
        # 8. CONVERTIR A LISTA Y VALIDAR PRECIOS (segunda capa de seguridad)
        repuestos_lista = []
        for repuesto in repuestos.distinct().order_by('-fecha_publicacion').iterator():
            try:
                precio = repuesto.precio
                if precio is not None and precio != '':
                    repuestos_lista.append(repuesto)
            except (ValueError, InvalidOperation, TypeError):
                print(f"[WARN] Repuesto con precio inválido saltado: {repuesto.id}")
                continue
        
        print(f"[DEBUG] Total repuestos válidos finales: {len(repuestos_lista)}")
        return repuestos_lista
        
    except Exception as e:
        print(f"[ERROR] Error en buscar_repuestos_compatibles: {str(e)}")
        import traceback
        traceback.print_exc()
        return []