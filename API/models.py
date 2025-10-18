from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
import math

""" CLIENTES """
class Cliente(models.Model):
    OPCIONES_FRECUENCIA = (
        ('OC', 'Ocasional'),
        ('RE', 'Regular'),
        ('FR', 'Frecuente'),
    )
    descripcion_referencia = models.CharField(max_length=100, verbose_name="Descripción de referencia")
    tipo_frecuencia = models.CharField(max_length=2, choices=OPCIONES_FRECUENCIA, default='OC')
    preferencias = models.TextField(blank=True, null=True, verbose_name="Preferencias")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"{self.descripcion_referencia}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['descripcion_referencia']


""" PRODUCTOS """
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creada en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizada en")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos', verbose_name="Categoría")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    codigo_barras = models.CharField(max_length=50, blank=True, null=True, verbose_name="Código de barras")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de compra")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de venta")
    stock_actual = models.IntegerField(default=0, verbose_name="Stock actual")
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock mínimo")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"{self.nombre} - ${self.precio_venta} (Stock: {self.stock_actual})"

    @property
    def needs_restock(self):
        return self.stock_actual <= self.stock_minimo

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']


class MovimientoStock(models.Model):
    TIPO_MOVIMIENTO = (
        ('IN', 'Ingreso'),
        ('SA', 'Salida'),
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos', verbose_name="Producto")
    tipo = models.CharField(max_length=2, choices=TIPO_MOVIMIENTO, verbose_name="Tipo de movimiento")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    motivo = models.CharField(max_length=100, verbose_name="Motivo")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movimientos_stock', verbose_name="Registrado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.producto.nombre}: {self.cantidad}"

    def save(self, *args, **kwargs):
        if self.tipo == 'IN':
            self.producto.stock_actual += self.cantidad
        elif self.tipo == 'SA':
            self.producto.stock_actual -= self.cantidad

        self.producto.save(update_fields=['stock_actual'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-created_at']


""" MESAS """
class TipoMesa(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    precio_por_hora = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por hora")
    precio_por_fraccion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por fracción (15 min)")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = "Tipo de Mesa"
        verbose_name_plural = "Tipos de Mesa"
        ordering = ['nombre']


class Mesa(models.Model):
    OPCIONES_ESTADO = (
        ('LI', 'Libre'),
        ('OC', 'Ocupada'),
        ('RE', 'Reservada'),
        ('ME', 'Mantenimiento'),
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    codigo = models.CharField(max_length=5, unique=True, verbose_name="Código")
    tipo = models.ForeignKey(TipoMesa, on_delete=models.CASCADE, related_name='mesas', verbose_name="Tipo")
    estado = models.CharField(max_length=2, choices=OPCIONES_ESTADO, default='LI', verbose_name="Estado")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    @property
    def alquiler_activo(self):
        return self.alquileres.filter(estado='AC').first()

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['nombre']


""" FINANZAS """
class MetodoPago(models.Model):
    METODO_PAGO = (
        ('EF', 'Efectivo'),
        ('TC', 'Tarjeta Crédito'),
        ('TD', 'Tarjeta Débito'),
        ('TR', 'Transferencia'),
        ('OT', 'Otro')
    )
    nombre = models.CharField(max_length=2, choices=METODO_PAGO, verbose_name="Nombre")
    requiere_referencia = models.BooleanField(default=False, verbose_name="Requiere referencia")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return self.get_nombre_display()

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['nombre']


class CierreCaja(models.Model):
    fecha_apertura = models.DateTimeField(verbose_name="Fecha y hora de apertura")
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y hora de cierre")
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto inicial")
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto final")
    ventas_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total de ventas")
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Diferencia")
    usuario_apertura = models.ForeignKey(User, on_delete=models.PROTECT, related_name='aperturas_caja', verbose_name="Usuario de apertura")
    usuario_cierre = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name='cierres_caja', verbose_name="Usuario de cierre")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"Caja #{self.id} - {self.fecha_apertura.strftime('%d/%m/%Y %H:%M')}"

    @property
    def esta_cerrada(self):
        return self.fecha_cierre is not None

    @property
    def calcular_ventas_totales(self):
        total = self.pagos.filter(estado='CO').aggregate(total=Sum('monto'))['total'] or 0
        return total

    class Meta:
        verbose_name = "Cierre de Caja"
        verbose_name_plural = "Cierres de Caja"
        ordering = ['-fecha_apertura']


""" ALQUILERES """


class Alquiler(models.Model):
    TIPO_ALQUILER = (
        (1, 'Limitado'),
        (2, 'Libre')
    )

    TIEMPO_ALQUILER = [
        (5, '5 minutos'),
        (10, '10 minutos'),
        (15, '15 minutos'),
        (20, '20 minutos'),
        (25, '25 minutos'),
        (30, '1/2 hora | 30 minutos'),
        (35, '35 minutos'),
        (40, '40 minutos'),
        (45, '45 minutos'),
        (50, '50 minutos'),
        (55, '55 minutos'),
        (60, '1 hora | 60 minutos'),
        (75, '1:15 horas | 75 minutos'),
        (90, '1:30 horas | 90 minutos'),
        (105, '1:45 horas | 105 minutos'),
        (120, '2 horas | 120 minutos'),
        (150, '2:30 horas | 150 minutos'),
        (180, '3 horas | 180 minutos'),
        (0, 'Libre')
    ]

    ESTADO_ALQUILER = (
        ('AC', 'Activo'),
        ('FI', 'Finalizado'),
        ('CA', 'Cancelado'),
        ('TR', 'Transferido')
    )

    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='alquileres', verbose_name="Mesa")
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, related_name='alquileres', verbose_name="Cliente", null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='alquileres', verbose_name="Usuario")
    tiempo_inicio = models.DateTimeField(verbose_name="Hora de inicio")
    tiempo_finalizacion = models.DateTimeField(null=True, blank=True, verbose_name="Hora de finalización")
    tiempo_finalizacion_programada = models.DateTimeField(null=True, blank=True, verbose_name="Hora de finalización programada")
    tipo_tiempo = models.IntegerField(choices=TIPO_ALQUILER, verbose_name="Tipo de tiempo", default=1)
    tiempo_asignado = models.IntegerField(verbose_name="Tiempo asignado (minutos)", choices=TIEMPO_ALQUILER, validators=[MinValueValidator(0)])
    monto_alquiler = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de alquiler", default=0, validators=[MinValueValidator(0)])
    descuento = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Descuento", default=0, validators=[MinValueValidator(0)])
    estado = models.CharField(max_length=2, choices=ESTADO_ALQUILER, default='AC', verbose_name="Estado del alquiler")
    mesa_anterior = models.ForeignKey(Mesa, on_delete=models.SET_NULL, related_name='alquileres_previos', null=True, blank=True, verbose_name="Mesa anterior")
    notas = models.TextField(verbose_name="Notas", blank=True, null=True)
    cierre_caja = models.ForeignKey(CierreCaja, on_delete=models.SET_NULL, null=True, blank=True, related_name='alquileres', verbose_name="Cierre de caja")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"{self.mesa} - {self.tiempo_inicio.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.pk and self.estado == 'AC':
            self.mesa.estado = 'OC'
            self.mesa.save(update_fields=['estado'])

            if self.tipo_tiempo == 1 and self.tiempo_asignado > 0:
                self.tiempo_finalizacion_programada = self.tiempo_inicio + timezone.timedelta(
                    minutes=self.tiempo_asignado)

        elif self.estado in ['FI', 'CA'] and 'estado' in kwargs.get('update_fields', []):
            self.mesa.estado = 'LI'
            self.mesa.save(update_fields=['estado'])

        super().save(*args, **kwargs)

    @property
    def monto_consumo(self):
        total = self.consumos.aggregate(total=Sum('subtotal'))['total'] or 0
        return total

    @property
    def monto_total(self):
        return self.monto_alquiler + self.monto_consumo - self.descuento

    @property
    def tiempo_transcurrido(self):
        fin = self.tiempo_finalizacion or timezone.now()
        delta = fin - self.tiempo_inicio
        minutos = delta.total_seconds() / 60
        return math.ceil(minutos)

    @property
    def tiempo_restante(self):
        if self.estado != 'AC' or self.tipo_tiempo != 1 or not self.tiempo_finalizacion_programada:
            return 0

        delta = self.tiempo_finalizacion_programada - timezone.now()
        minutos = delta.total_seconds() / 60
        return max(0, math.ceil(minutos))

    @property
    def esta_pagado(self):
        pagado = self.pagos.filter(estado='CO').aggregate(total=Sum('monto'))['total'] or 0
        return round(pagado, 2) >= round(self.monto_total, 2)

    class Meta:
        verbose_name = "Alquiler"
        verbose_name_plural = "Alquileres"
        ordering = ['-tiempo_inicio']


class Consumo(models.Model):
    alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE, related_name='consumos', verbose_name="Alquiler")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='consumos', verbose_name="Producto")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consumos_registrados', verbose_name="Registrado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    def __str__(self):
        return f"Consumo: {self.cantidad} x {self.producto.nombre} - {self.alquiler}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario

        crear_movimiento = not self.pk  # Solo si es nuevo

        super().save(*args, **kwargs)

        if crear_movimiento:
            MovimientoStock.objects.create(
                producto=self.producto,
                tipo='SA',
                cantidad=self.cantidad,
                motivo=f"Consumo en alquiler #{self.alquiler.id}",
                usuario=self.usuario
            )

    class Meta:
        verbose_name = "Consumo"
        verbose_name_plural = "Consumos"
        ordering = ['-created_at']


class TransferenciaAlquiler(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transferencias', verbose_name="Usuario")
    alquiler_origen = models.ForeignKey(Alquiler, on_delete=models.CASCADE, related_name='transferencias_origen', verbose_name="Alquiler origen")
    alquiler_destino = models.ForeignKey(Alquiler, on_delete=models.CASCADE, related_name='transferencias_destino', verbose_name="Alquiler destino")
    mesa_origen = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='transferencias_origen', verbose_name="Mesa origen")
    mesa_destino = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='transferencias_destino', verbose_name="Mesa destino")
    tiempo_transferencia = models.DateTimeField(auto_now_add=True, verbose_name="Hora de transferencia")
    tiempo_restante = models.IntegerField(verbose_name="Tiempo restante (minutos)", default=0)
    notas = models.TextField(verbose_name="Notas", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"Transferencia: {self.mesa_origen} → {self.mesa_destino} ({self.tiempo_transferencia.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = "Transferencia de Alquiler"
        verbose_name_plural = "Transferencias de Alquileres"
        ordering = ['-tiempo_transferencia']


class Pago(models.Model):
    ESTADO_OPCIONES = [
        ('CO', 'Completado'),
        ('CA', 'Cancelado'),
    ]

    alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE, related_name='pagos', verbose_name="Alquiler")
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name="Fecha y hora")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='pagos', verbose_name="Método de pago")
    referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referencia")
    estado = models.CharField(max_length=2, choices=ESTADO_OPCIONES, default='CO', verbose_name="Estado")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pagos_registrados', verbose_name="Procesado por")
    cierre_caja = models.ForeignKey(CierreCaja, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos', verbose_name="Cierre de caja")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"Pago: ${self.monto} - {self.metodo_pago.get_nombre_display()} - {self.alquiler}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_hora']


""" VENTAS DIRECTAS """
class VentaDirecta(models.Model):
    ESTADO_VENTA = [
        ('CO', 'Completada'),
        ('CA', 'Cancelada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, related_name='ventas', verbose_name="Cliente", null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ventas', verbose_name="Usuario")
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name="Fecha y hora")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal", default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Descuento", default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total", default=0)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='ventas', verbose_name="Método de pago")
    referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referencia")
    estado = models.CharField(max_length=2, choices=ESTADO_VENTA, default='CO', verbose_name="Estado")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    cierre_caja = models.ForeignKey(CierreCaja, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas', verbose_name="Cierre de caja")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        self.total = self.subtotal - self.descuento
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Venta Directa"
        verbose_name_plural = "Ventas Directas"
        ordering = ['-fecha_hora']


class DetalleVenta(models.Model):
    venta = models.ForeignKey(VentaDirecta, on_delete=models.CASCADE, related_name='detalles', verbose_name="Venta")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ventas', verbose_name="Producto")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario

        crear_movimiento = not self.pk

        super().save(*args, **kwargs)

        self.venta.subtotal = self.venta.detalles.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        self.venta.save(update_fields=['subtotal', 'total'])

        if crear_movimiento:
            MovimientoStock.objects.create(
                producto=self.producto,
                tipo='SA',
                cantidad=self.cantidad,
                motivo=f"Venta directa #{self.venta.id}",
                usuario=self.venta.usuario
            )

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        ordering = ['id']


""" COMPRAS Y PROVEEDORES """
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contacto")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']


class Compra(models.Model):
    ESTADO_COMPRA = [
        ('RE', 'Recibida'),
        ('PE', 'Pendiente'),
        ('CA', 'Cancelada'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras', verbose_name="Proveedor")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='compras', verbose_name="Usuario")
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name="Fecha y hora")
    numero_factura = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de factura")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total", default=0)
    estado = models.CharField(max_length=2, choices=ESTADO_COMPRA, default='RE', verbose_name="Estado")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor} ({self.fecha_hora.strftime('%d/%m/%Y')})"

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha_hora']


class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles', verbose_name="Compra")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='compras', verbose_name="Producto")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario

        crear_movimiento = not self.pk and self.compra.estado == 'RE'

        super().save(*args, **kwargs)

        self.compra.total = self.compra.detalles.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        self.compra.save(update_fields=['total'])

        if crear_movimiento:
            MovimientoStock.objects.create(
                producto=self.producto,
                tipo='IN',
                cantidad=self.cantidad,
                motivo=f"Compra #{self.compra.id}",
                usuario=self.compra.usuario
            )

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"
        ordering = ['id']


""" NOTIFICACIONES Y ALERTAS """
class Notificacion(models.Model):
    TIPO_NOTIFICACION = [
        ('AL', 'Alerta'),
        ('IN', 'Información'),
        ('EX', 'Éxito'),
        ('ER', 'Error')
    ]

    ESTADO_NOTIFICACION = [
        ('PE', 'Pendiente'),
        ('LE', 'Leída'),
        ('AR', 'Archivada')
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones', verbose_name="Usuario")
    tipo = models.CharField(max_length=2, choices=TIPO_NOTIFICACION, default='IN', verbose_name="Tipo")
    titulo = models.CharField(max_length=100, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    enlace = models.CharField(max_length=200, blank=True, null=True, verbose_name="Enlace")
    estado = models.CharField(max_length=2, choices=ESTADO_NOTIFICACION, default='PE', verbose_name="Estado")
    fecha_lectura = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de lectura")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-created_at']


""" CONFIGURACIÓN """
class Configuracion(models.Model):
    clave = models.CharField(max_length=50, unique=True, verbose_name="Clave")
    valor = models.TextField(verbose_name="Valor")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    modificable = models.BooleanField(default=True, verbose_name="Modificable")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"{self.clave}: {self.valor}"

    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"
        ordering = ['clave']


""" ESTADÍSTICAS Y REPORTES """
class EstadisticasDiarias(models.Model):
    fecha = models.DateField(unique=True, verbose_name="Fecha")
    ventas_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ventas totales")
    ventas_alquiler = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ventas por alquiler")
    ventas_productos = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ventas de productos")
    numero_alquileres = models.IntegerField(default=0, verbose_name="Número de alquileres")
    numero_ventas = models.IntegerField(default=0, verbose_name="Número de ventas")
    tiempo_total_alquiler = models.IntegerField(default=0, verbose_name="Tiempo total de alquiler (minutos)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    def __str__(self):
        return f"Estadísticas del {self.fecha.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Estadística Diaria"
        verbose_name_plural = "Estadísticas Diarias"
        ordering = ['-fecha']