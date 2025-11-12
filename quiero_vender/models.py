from django.db import models

class SolicitudCompra(models.Model):
    URGENCIA_CHOICES = [
        ('baja', 'Baja - Puedo esperar'),
        ('media', 'Media - Lo necesito pronto'),
        ('alta', 'Alta - Urgente'),
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
    categoria_repuesto = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, verbose_name="Categoría del Repuesto")
    repuesto_especifico = models.CharField(max_length=200, verbose_name="Repuesto Específico")
    descripcion_adicional = models.TextField(verbose_name="Descripción Adicional", blank=True)
    urgencia = models.CharField(max_length=20, choices=URGENCIA_CHOICES, verbose_name="Nivel de Urgencia")
    
    # Datos personales
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Email")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    dni = models.CharField(max_length=20, verbose_name="DNI")
    
    # Metadata
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Solicitud de Compra"
        verbose_name_plural = "Solicitudes de Compra"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.repuesto_especifico}"


class PublicacionVenta(models.Model):
    ESTADO_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('usado_excelente', 'Usado - Excelente'),
        ('usado_bueno', 'Usado - Bueno'),
        ('usado_regular', 'Usado - Regular'),
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
    
    # Datos del repuesto
    titulo = models.CharField(max_length=200, verbose_name="Título del Repuesto")
    marca_auto = models.CharField(max_length=100, verbose_name="Marca del Auto Compatible")
    modelo_auto = models.CharField(max_length=100, verbose_name="Modelo Compatible", blank=True)
    año_desde = models.IntegerField(verbose_name="Año Desde", null=True, blank=True)
    año_hasta = models.IntegerField(verbose_name="Año Hasta", null=True, blank=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, verbose_name="Categoría")
    descripcion = models.TextField(verbose_name="Descripción del Repuesto")
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, verbose_name="Estado")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    
    # Datos del vendedor
    nombre_vendedor = models.CharField(max_length=200, verbose_name="Nombre del Vendedor")
    email_vendedor = models.EmailField(verbose_name="Email")
    telefono_vendedor = models.CharField(max_length=20, verbose_name="Teléfono")
    ubicacion = models.CharField(max_length=200, verbose_name="Ubicación")
    
    # Metadata
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    disponible = models.BooleanField(default=True)
    vistas = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Publicación de Venta"
        verbose_name_plural = "Publicaciones de Venta"
        ordering = ['-fecha_publicacion']
    
    def __str__(self):
        return f"{self.titulo} - ${self.precio}"