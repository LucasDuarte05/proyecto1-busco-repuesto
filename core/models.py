from django.db import models
from django.contrib.auth.models import User

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
    celular = models.CharField(max_length=20, verbose_name="Celular", default='')
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
    
    @property
    def telefono(self):
        return self.celular


# ✅ NUEVO MODELO PARA MÚLTIPLES IMÁGENES
class ImagenRepuesto(models.Model):
    solicitud = models.ForeignKey(
        SolicitudCompra, 
        on_delete=models.CASCADE, 
        related_name='imagenes'
    )
    imagen = models.ImageField(
        upload_to='repuestos_fotos/',
        verbose_name="Imagen del Repuesto"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Imagen de Repuesto"
        verbose_name_plural = "Imágenes de Repuestos"
        ordering = ['fecha_subida']
    
    def __str__(self):
        return f"Imagen de {self.solicitud.repuesto_especifico}"


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
    
    # Coordenadas GPS
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


class VendedorEmpresa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendedor_empresa')
    nombre_empresa = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    cuit = models.CharField(max_length=13, verbose_name="CUIT", unique=True)
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    direccion = models.CharField(max_length=300, verbose_name="Dirección")
    localidad = models.CharField(max_length=200, verbose_name="Localidad")
    provincia = models.CharField(max_length=200, verbose_name="Provincia")
    web_ig = models.CharField(max_length=200, verbose_name="Web/Instagram", blank=True)
    
    latitud = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Latitud", null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Longitud", null=True, blank=True)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Vendedor Empresa"
        verbose_name_plural = "Vendedores Empresas"
    
    def __str__(self):
        return f"{self.nombre_empresa} - {self.cuit}"


class Cotizacion(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente de revisión"),
        ("enviada", "Enviada al cliente"),
        ("rechazada", "Rechazada"),
        ("cliente_interesado", "Cliente interesado"),
    ]

    solicitud = models.ForeignKey(
        SolicitudCompra,
        on_delete=models.CASCADE,
        related_name="cotizaciones"
    )
    
    vendedor = models.ForeignKey(
        VendedorEmpresa,
        on_delete=models.CASCADE,
        related_name="cotizaciones"
    )
    
    precio = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio")
    comentarios = models.TextField(blank=True, verbose_name="Comentarios")
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="pendiente",
        verbose_name="Estado"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        unique_together = ['solicitud', 'vendedor']
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Cotización #{self.id} - {self.vendedor.nombre_empresa} - ${self.precio}"