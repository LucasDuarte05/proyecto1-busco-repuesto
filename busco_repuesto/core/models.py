from django.db import models

class SolicitudCompra(models.Model):
    URGENCIA_CHOICES = [
        ('baja', 'Baja - Puedo esperar'),
        ('media', 'Media - Lo necesito pronto'),
        ('alta', 'Alta - Urgente'),
        ('super_alta', 'Super Alta - Muy Urgente (en hora)'),
    ]
    
    CATEGORIA_CHOICES = [
        ('motor', 'Motor'),
        ('transmision', 'Transmisión'),
        ('suspension', 'Suspensión'),
        ('frenos', 'Frenos'),
        ('electrico', 'Sistema Eléctrico'),
        ('carroceria', 'Carrocería'),
        ('interior', 'Interior'),
        ('otros', 'Otros'),
    ]
    
    # Datos del vehículo y repuesto
    marca_auto = models.CharField(max_length=100, verbose_name="Marca del Auto")
    modelo_auto = models.CharField(max_length=100, verbose_name="Modelo del Auto", blank=True)
    año_auto = models.IntegerField(verbose_name="Año del Auto", null=True, blank=True)
    nro_chasis = models.CharField(max_length=100, verbose_name="VIN/Número de Chasis", blank=True, default='')
    categoria_repuesto = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, verbose_name="Categoría del Repuesto")
    repuesto_especifico = models.CharField(max_length=200, verbose_name="Repuesto Específico")
    descripcion_adicional = models.TextField(verbose_name="Descripción Adicional", blank=True)
    urgencia = models.CharField(max_length=20, choices=URGENCIA_CHOICES, verbose_name="Nivel de Urgencia")
    
    # Datos personales
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Email")  # ✅ CAMPO EMAIL
    celular = models.CharField(max_length=20, verbose_name="Celular")  # También puede ser "telefono"
    localidad = models.CharField(max_length=200, verbose_name="Localidad", blank=True, default='')
    zona = models.CharField(max_length=200, verbose_name="Zona/Provincia", blank=True, default='')
    
    # Metadata
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Solicitud de Compra"
        verbose_name_plural = "Solicitudes de Compra"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.nombre} - {self.repuesto_especifico}"
    
    # Propiedad para compatibilidad con código antiguo
    @property
    def telefono(self):
        return self.celular


class PublicacionVenta(models.Model):
    ESTADO_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('usado_excelente', 'Usado - Excelente'),
        ('usado_bueno', 'Usado - Bueno'),
        ('usado_regular', 'Usado - Regular'),
    ]
    
    # Datos del vendedor
    nombre_vendedor = models.CharField(max_length=200, verbose_name="Nombre del Vendedor")
    email_vendedor = models.EmailField(verbose_name="Email")
    telefono_vendedor = models.CharField(max_length=20, verbose_name="Teléfono")
    
    # CAMPOS DE UBICACIÓN CON DIRECCIÓN EXACTA
    zona = models.CharField(max_length=200, verbose_name="Zona/Provincia", blank=True, default='')
    localidad = models.CharField(max_length=200, verbose_name="Localidad", blank=True, default='')
    direccion = models.CharField(max_length=300, verbose_name="Dirección", blank=True, default='')
    ubicacion = models.CharField(max_length=200, verbose_name="Ubicación", blank=True, default='')
    
    # Coordenadas GPS (se calculan automáticamente desde la dirección)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Latitud", null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Longitud", null=True, blank=True)
    
    # Metadata
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    disponible = models.BooleanField(default=True)
    vistas = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Publicación de Venta"
        verbose_name_plural = "Publicaciones de Venta"
        ordering = ['-fecha_publicacion']
    
    def __str__(self):
        return f"{self.nombre_vendedor} - {self.direccion or self.ubicacion}"
    
    def get_ubicacion_completa(self):
        """Retorna la ubicación completa en formato legible"""
        partes = []
        if self.direccion:
            partes.append(self.direccion)
        if self.localidad:
            partes.append(self.localidad)
        if self.zona:
            partes.append(self.zona)
        
        if partes:
            return ", ".join(partes)
        return self.ubicacion