from core.models import PublicacionVenta
from decimal import Decimal, InvalidOperation

def limpiar_precios_invalidos():
    """
    Limpia o elimina repuestos con precios inválidos
    """
    print("=" * 50)
    print("INICIANDO LIMPIEZA DE PRECIOS INVÁLIDOS")
    print("=" * 50)
    
    # Obtener TODOS los repuestos
    todos_repuestos = PublicacionVenta.objects.all()
    total = todos_repuestos.count()
    
    print(f"\nTotal de repuestos en la base de datos: {total}")
    
    invalidos = []
    validos = 0
    
    # Revisar cada repuesto
    for repuesto in todos_repuestos:
        try:
            # Intentar acceder al precio
            precio = repuesto.precio
            
            # Verificar que no sea None, vacío o inválido
            if precio is None or precio == '':
                invalidos.append(repuesto)
            else:
                # Intentar convertir a Decimal
                Decimal(str(precio))
                validos += 1
        except (ValueError, InvalidOperation, TypeError) as e:
            invalidos.append(repuesto)
    
    print(f"RESULTADOS:")
    print(f"Repuestos con precio válido: {validos}")
    print(f"Repuestos con precio inválido: {len(invalidos)}")
    
    if len(invalidos) > 0:
        print(f"REPUESTOS CON PRECIOS INVÁLIDOS:")
        print("-" * 50)
        
        for rep in invalidos[:10]:  # Mostrar solo los primeros 10
            try:
                precio_raw = rep.__dict__.get('precio', 'N/A')
                print(f"ID: {rep.id} | Título: {rep.titulo[:40]} | Precio: '{precio_raw}'")
            except:
                print(f"ID: {rep.id} | Error al leer datos")
        
        if len(invalidos) > 10:
            print(f"... y {len(invalidos) - 10} más")
        
        print("\n" + "=" * 50)
        print("OPCIONES DE LIMPIEZA:")
        print("=" * 50)
        print("\n1  MARCAR COMO NO DISPONIBLES (recomendado)")
        print("Los repuestos se mantienen pero no aparecerán en búsquedas")
        print("\n2  ELIMINAR PERMANENTEMENTE")
        print("Los repuestos se borran de la base de datos")
        print("\n3CANCELAR")
        print("No hacer nada")
        
        opcion = input("\n Selecciona una opción (1/2/3): ").strip()
        
        if opcion == '1':
            print("\Marcando repuestos como no disponibles...")
            count = 0
            for rep in invalidos:
                rep.disponible = False
                rep.save()
                count += 1
            print(f" {count} repuestos marcados como no disponibles")
            
        elif opcion == '2':
            confirmacion = input("\n  ¿ESTÁS SEGURO? Esta acción NO se puede deshacer (SI/NO): ").strip().upper()
            if confirmacion == 'SI':
                print("\n  Eliminando repuestos...")
                ids_eliminar = [rep.id for rep in invalidos]
                PublicacionVenta.objects.filter(id__in=ids_eliminar).delete()
                print(f" {len(ids_eliminar)} repuestos eliminados")
            else:
                print(" Eliminación cancelada")
                
        elif opcion == '3':
            print(" Operación cancelada")
        else:
            print(" Opción inválida")
    else:
        print("\n ¡PERFECTO! No hay repuestos con precios inválidos")
    
    print("\n" + "=" * 50)
    print("LIMPIEZA FINALIZADA")
    print("=" * 50)

# Ejecutar si se corre como script
if __name__ == '__main__':
    limpiar_precios_invalidos()
else:
    # Si se importa, ejecutar automáticamente
    limpiar_precios_invalidos()