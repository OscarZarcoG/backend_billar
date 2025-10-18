# POS/models.py
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models import Sum, F
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal
from CLIENTS.models import  Customer

""" B A S E   M O D E L  ✔ """
class BaseModel(models.Model):
    status = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Eliminado en")

    class Meta:
        abstract = True

    def soft_delete(self):
        self.status = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.status = True
        self.deleted_at = None
        self.save()


""" C A T E G O R I A S  ✔ """
class Categoria(BaseModel):
    nombre = models.CharField(max_length=100, verbose_name="Nombre", unique=True)
    descripcion = models.CharField(max_length=255, verbose_name="Descripción", blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]


""" M A R C A S  Y   E M P R E S A S  ✔ """
class Marca_Empresa(BaseModel):
    nombre = models.CharField(max_length=100, verbose_name="Nombre", unique=True)
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True, verbose_name="Logo")
    sitio_web = models.URLField(blank=True, null=True, verbose_name="Sitio Web")
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Marca_Empresa"
        verbose_name_plural = "Marcas_Empresas"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]


""" P R O V E E D O R E S  ✔ """
class Proveedores(BaseModel):
    nombre = models.CharField(max_length=100, verbose_name="Nombre", unique=True)
    empresa = models.ForeignKey(Marca_Empresa, on_delete=models.PROTECT, related_name='proveedores', verbose_name="Empresa")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.telefono and not self.telefono.isdigit():
            raise ValidationError({'telefono': 'El teléfono debe contener solo dígitos'})
        if self.telefono and len(self.telefono) < 10:
            raise ValidationError({'telefono': 'El teléfono debe tener al menos 10 dígitos'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['telefono']),
        ]


""" P R O D U C T O S  ✔ """
class Producto(BaseModel):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    codigo_barras = models.CharField(max_length=20, verbose_name="Código de barras", unique=True, db_index=True)
    sku = models.CharField(max_length=50, verbose_name="SKU", unique=True, blank=True, null=True)
    marca = models.ForeignKey(Marca_Empresa, on_delete=models.PROTECT, related_name='productos', verbose_name="Marca")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos', verbose_name="Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de compra", validators=[MinValueValidator(0.01)])
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de venta", validators=[MinValueValidator(0.01)])
    margen_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Margen de ganancia (%)")
    proveedor_principal = models.ForeignKey(Proveedores, on_delete=models.SET_NULL, related_name='productos_suministrados', verbose_name="Proveedor principal",  blank=True, null=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen")
    stock_actual = models.IntegerField(default=0, verbose_name="Stock actual")
    stock_minimo = models.IntegerField(default=3, verbose_name="Stock mínimo")
    stock_maximo = models.IntegerField(default=100, verbose_name="Stock máximo")
    peso = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True, verbose_name="Peso (kg)")
    dimensiones = models.CharField(max_length=50, blank=True, null=True, verbose_name="Dimensiones (LxAxA)")
    es_servicio = models.BooleanField(default=False, verbose_name="Es servicio")
    impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Impuesto (%)")

    def __str__(self):
        return f"{self.nombre} - {self.marca}"

    @property
    def ganancia_absoluta(self):
        if self.precio_venta is not None and self.precio_compra is not None:
            return self.precio_venta - self.precio_compra
        return Decimal('0.00')

    @property
    def ganancia_porcentual(self):
        if self.precio_compra is not None and self.precio_compra > 0 and self.precio_venta is not None:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0

    @property
    def exceso_stock(self):
        if self.stock_actual is not None and self.stock_maximo is not None:
            return self.stock_actual > self.stock_maximo
        return False

    @property
    def requiere_reposicion(self):
        if self.stock_actual is not None and self.stock_minimo is not None and not self.es_servicio:
            return self.stock_actual <= self.stock_minimo
        return False

    @property
    def disponible(self):
        disponible_por_stock = (self.stock_actual is not None and self.stock_actual > 0) or self.es_servicio
        return disponible_por_stock and self.status

    @property
    def precio_con_impuesto(self):
        if self.precio_venta is not None:
            return self.precio_venta * (1 + (self.impuesto or 0) / 100)
        return Decimal('0.00')

    def actualizar_precio_venta_por_margen(self):
        if self.margen_ganancia is not None and self.margen_ganancia > 0 and self.precio_compra is not None:
            self.precio_venta = self.precio_compra * (1 + self.margen_ganancia / 100)

    def clean(self):
        if (self.precio_venta is not None and self.precio_compra is not None and
                self.precio_venta < self.precio_compra):
            raise ValidationError({'precio_venta': 'El precio de venta no puede ser menor al precio de compra'})

        if (self.stock_maximo is not None and self.stock_minimo is not None and
                self.stock_maximo < self.stock_minimo):
            raise ValidationError({'stock_maximo': 'El stock máximo debe ser mayor al stock mínimo'})

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.marca.nombre[:3].upper()}-{self.codigo_barras[-6:]}"
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['sku']),
            models.Index(fields=['nombre']),
            models.Index(fields=['categoria', 'marca']),
            models.Index(fields=['stock_actual']),
        ]


""" M O V I M I E N T O S  D E  S T O C K """
class MovimientoStock(BaseModel):
    TIPO_MOVIMIENTO = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
        ('MERMA', 'Merma'),
        ('DEVOLUCION', 'Devolución'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos', verbose_name="Producto")
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO, verbose_name="Tipo de movimiento")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    stock_anterior = models.IntegerField(verbose_name="Stock anterior")
    stock_nuevo = models.IntegerField(verbose_name="Stock nuevo")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movimientos_stock', verbose_name="Usuario")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referencia")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} de {self.producto.nombre}: {self.cantidad} unidades"

    @classmethod
    def crear_movimiento(cls, producto, tipo_movimiento, cantidad, usuario, precio_unitario, referencia=None,
                         observaciones=None):
        with transaction.atomic():
            stock_anterior = producto.stock_actual

            if tipo_movimiento == 'ENTRADA':
                stock_nuevo = stock_anterior + cantidad
            elif tipo_movimiento == 'SALIDA':
                if stock_anterior < cantidad and not producto.es_servicio:
                    raise ValidationError(f'Stock insuficiente. Disponible: {stock_anterior}')
                stock_nuevo = stock_anterior - cantidad
            elif tipo_movimiento == 'AJUSTE':
                stock_nuevo = cantidad
                cantidad = cantidad - stock_anterior
            elif tipo_movimiento in ['MERMA', 'DEVOLUCION']:
                stock_nuevo = stock_anterior - cantidad
            else:
                stock_nuevo = stock_anterior

            movimiento = cls.objects.create(
                producto=producto,
                tipo_movimiento=tipo_movimiento,
                cantidad=abs(cantidad),
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                usuario=usuario,
                precio_unitario=precio_unitario,
                referencia=referencia,
                observaciones=observaciones
            )

            producto.stock_actual = stock_nuevo
            producto.save()

            return movimiento

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['producto']),
            models.Index(fields=['fecha']),
            models.Index(fields=['tipo_movimiento']),
            models.Index(fields=['referencia']),
        ]


""" C O M P R A S """
class Compra(BaseModel):
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('RECIBIDA', 'Recibida'),
        ('CANCELADA', 'Cancelada'),
    )

    numero_factura = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de factura")
    proveedor = models.ForeignKey(Proveedores, on_delete=models.PROTECT, related_name='compras', verbose_name="Proveedor")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='compras', verbose_name="Usuario")
    fecha_pedido = models.DateField(auto_now_add=True, verbose_name="Fecha de pedido")
    fecha_recepcion = models.DateField(blank=True, null=True, verbose_name="Fecha de recepción")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento")
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impuesto")

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre} ({self.fecha_pedido})"

    @property
    def subtotal(self):
        return self.detalles.aggregate(
            total=Coalesce(Sum(F('cantidad') * F('precio_unitario')), Decimal('0.00'))
        )['total']

    @property
    def total(self):
        subtotal = self.subtotal
        return subtotal - self.descuento + self.impuesto

    @property
    def cantidad_items(self):
        return self.detalles.aggregate(total=Coalesce(Sum('cantidad'), 0))['total']

    def marcar_como_recibida(self):
        if self.estado != 'RECIBIDA':
            self.estado = 'RECIBIDA'
            self.fecha_recepcion = timezone.now().date()
            self.save()

            for detalle in self.detalles.all():
                MovimientoStock.crear_movimiento(
                    producto=detalle.producto,
                    tipo_movimiento='ENTRADA',
                    cantidad=detalle.cantidad,
                    usuario=self.usuario,
                    precio_unitario=detalle.precio_unitario,
                    referencia=f"Compra #{self.id}"
                )

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha_pedido', '-id']
        indexes = [
            models.Index(fields=['fecha_pedido']),
            models.Index(fields=['proveedor']),
            models.Index(fields=['estado']),
            models.Index(fields=['numero_factura']),
        ]


""" D E T A L L E S  C O M P R A S """
class DetalleCompra(BaseModel):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles', verbose_name="Compra")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='compras', verbose_name="Producto")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad", validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario", validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad}) - Compra #{self.compra.id}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.precio_unitario != self.producto.precio_compra:
            self.producto.precio_compra = self.precio_unitario
            self.producto.save()

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"
        unique_together = ['compra', 'producto']
        indexes = [
            models.Index(fields=['compra']),
            models.Index(fields=['producto']),
        ]


""" V E N T A S """
class Venta(BaseModel):
    METODO_PAGO_CHOICES = (
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('MIXTO', 'Mixto'),
    )

    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('DEVUELTA', 'Devuelta'),
    )

    numero_ticket = models.CharField(max_length=20, unique=True, verbose_name="Número de ticket")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ventas', verbose_name="Usuario")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas', verbose_name="Cliente", blank=True, null=True)
    metodo_pago = models.CharField(max_length=15, choices=METODO_PAGO_CHOICES, default='EFECTIVO', verbose_name="Método de pago")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='COMPLETADA', verbose_name="Estado")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento")
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impuesto")
    observaciones = models.TextField(max_length=255, blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return f"Venta #{self.numero_ticket} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    @property
    def subtotal(self):
        return self.detalles.aggregate(
            total=Coalesce(Sum(F('cantidad') * F('precio_unitario')), Decimal('0.00'))
        )['total']

    @property
    def total(self):
        subtotal = self.subtotal
        return subtotal - self.descuento + self.impuesto

    @property
    def ganancia(self):
        return self.detalles.aggregate(
            ganancia=Coalesce(Sum((F('precio_unitario') - F('producto__precio_compra')) * F('cantidad')),
                              Decimal('0.00'))
        )['ganancia']

    @property
    def cantidad_items(self):
        return self.detalles.aggregate(total=Coalesce(Sum('cantidad'), 0))['total'] or 0

    def generar_numero_ticket(self):
        if not self.numero_ticket:
            ultimo_numero = Venta.objects.filter(
                fecha__date=self.fecha.date()
            ).exclude(id=self.id).aggregate(
                max_numero=models.Max('numero_ticket')
            )['max_numero']

            if ultimo_numero:
                numero = int(ultimo_numero.split('-')[-1]) + 1
            else:
                numero = 1

            self.numero_ticket = f"{self.fecha.strftime('%Y%m%d')}-{numero:04d}"

    def save(self, *args, **kwargs):
        if not self.numero_ticket:
            self.generar_numero_ticket()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['usuario']),
            models.Index(fields=['numero_ticket']),
            models.Index(fields=['estado']),
            models.Index(fields=['metodo_pago']),
        ]


""" D E T A L L E S  V E N T A S """
class DetalleVenta(BaseModel):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles', verbose_name="Venta")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta', verbose_name="Producto")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad", validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario", validators=[MinValueValidator(0.01)])
    descuento_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento por unidad")

    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad}) - Venta #{self.venta.numero_ticket}"

    @property
    def precio_con_descuento(self):
        return self.precio_unitario - self.descuento_unitario

    @property
    def subtotal(self):
        return self.cantidad * self.precio_con_descuento

    @property
    def ganancia(self):
        return (self.precio_con_descuento - self.producto.precio_compra) * self.cantidad

    def clean(self):
        if not self.producto.es_servicio and self.cantidad > self.producto.stock_actual:
            raise ValidationError({'cantidad': f'Stock insuficiente. Disponible: {self.producto.stock_actual}'})
        if self.descuento_unitario > self.precio_unitario:
            raise ValidationError({'descuento_unitario': 'El descuento no puede ser mayor al precio unitario'})

    def save(self, *args, **kwargs):
        self.clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.producto.es_servicio:
            MovimientoStock.crear_movimiento(
                producto=self.producto,
                tipo_movimiento='SALIDA',
                cantidad=self.cantidad,
                usuario=self.venta.usuario,
                precio_unitario=self.precio_unitario,
                referencia=f"Venta #{self.venta.numero_ticket}"
            )

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        unique_together = ['venta', 'producto']
        indexes = [
            models.Index(fields=['venta']),
            models.Index(fields=['producto']),
        ]


""" A L E R T A S  D E  S T O C K """
class AlertaStock(BaseModel):
    TIPO_ALERTA = (
        ('STOCK_BAJO', 'Stock Bajo'),
        ('SIN_STOCK', 'Sin Stock'),
        ('EXCESO_STOCK', 'Exceso de Stock'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='alertas', verbose_name="Producto")
    tipo_alerta = models.CharField(max_length=15, choices=TIPO_ALERTA, verbose_name="Tipo de alerta")
    mensaje = models.TextField(verbose_name="Mensaje")
    leida = models.BooleanField(default=False, verbose_name="Leída")
    usuario_asignado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_asignadas', verbose_name="Usuario asignado", blank=True, null=True)

    def __str__(self):
        return f"Alerta: {self.producto.nombre} - {self.get_tipo_alerta_display()}"

    @classmethod
    def generar_alertas_stock(cls):
        productos = Producto.objects.filter(status=True, es_servicio=False)

        for producto in productos:
            cls.objects.filter(producto=producto).delete()

            if producto.stock_actual == 0:
                cls.objects.create(
                    producto=producto,
                    tipo_alerta='SIN_STOCK',
                    mensaje=f'El producto {producto.nombre} está agotado'
                )
            elif producto.requiere_reposicion:
                cls.objects.create(
                    producto=producto,
                    tipo_alerta='STOCK_BAJO',
                    mensaje=f'El producto {producto.nombre} tiene stock bajo ({producto.stock_actual} unidades)'
                )
            elif producto.exceso_stock:
                cls.objects.create(
                    producto=producto,
                    tipo_alerta='EXCESO_STOCK',
                    mensaje=f'El producto {producto.nombre} tiene exceso de stock ({producto.stock_actual} unidades)'
                )

    class Meta:
        verbose_name = "Alerta de Stock"
        verbose_name_plural = "Alertas de Stock"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['producto']),
            models.Index(fields=['tipo_alerta']),
            models.Index(fields=['leida']),
        ]