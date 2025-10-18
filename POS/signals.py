# POS/signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal

from .models import (
    Producto, MovimientoStock, Venta, DetalleVenta,
    DetalleCompra, Compra, AlertaStock
)

""" S I G N A L S   P A R A   P R O D U C T O S """


@receiver(post_save, sender=Producto)
def producto_post_save(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta después de guardar un producto.
    - Genera alertas de stock si es necesario
    - Actualiza el precio de venta basado en el margen si está configurado
    """
    if created:
        # Crear movimiento inicial de stock si tiene stock_actual > 0
        if instance.stock_actual > 0 and not instance.es_servicio:
            try:
                # Buscar un usuario administrador para el movimiento inicial
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    MovimientoStock.crear_movimiento(
                        producto=instance,
                        tipo_movimiento='AJUSTE',
                        cantidad=instance.stock_actual,
                        usuario=admin_user,
                        precio_unitario=instance.precio_compra,
                        referencia="Stock inicial",
                        observaciones="Stock inicial del producto"
                    )
            except Exception:
                pass  # Si no se puede crear el movimiento, continuar

    # Actualizar precio de venta por margen si está configurado
    if instance.margen_ganancia > 0 and not kwargs.get('update_fields'):
        precio_calculado = instance.precio_compra * (1 + instance.margen_ganancia / 100)
        if precio_calculado != instance.precio_venta:
            # Actualizar solo el precio de venta para evitar recursión infinita
            Producto.objects.filter(id=instance.id).update(precio_venta=precio_calculado)

    # Generar alertas de stock
    generar_alerta_stock_producto(instance)


@receiver(pre_save, sender=Producto)
def producto_pre_save(sender, instance, **kwargs):
    """
    Señal que se ejecuta antes de guardar un producto.
    - Genera SKU automático si no existe
    """
    if not instance.sku and instance.marca and instance.codigo_barras:
        instance.sku = f"{instance.marca.nombre[:3].upper()}-{instance.codigo_barras[-6:]}"


""" S I G N A L S   P A R A   M O V I M I E N T O S   D E   S T O C K """


@receiver(post_save, sender=MovimientoStock)
def movimiento_stock_post_save(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta después de crear un movimiento de stock.
    - Genera alertas de stock actualizadas
    """
    if created:
        generar_alerta_stock_producto(instance.producto)


""" S I G N A L S   P A R A   V E N T A S """


@receiver(post_save, sender=Venta)
def venta_post_save(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta después de guardar una venta.
    - Genera número de ticket automático si no existe
    """
    if created and not instance.numero_ticket:
        instance.generar_numero_ticket()
        # Usar update para evitar recursión infinita
        Venta.objects.filter(id=instance.id).update(numero_ticket=instance.numero_ticket)


@receiver(post_save, sender=DetalleVenta)
def detalle_venta_post_save(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta después de guardar un detalle de venta.
    - Crea movimiento de stock automáticamente
    - Genera alertas de stock si es necesario
    """
    if created and instance.venta.estado == 'COMPLETADA':
        # El movimiento de stock ya se crea en el método save del modelo
        # Solo generar alerta de stock actualizada
        generar_alerta_stock_producto(instance.producto)


@receiver(post_delete, sender=DetalleVenta)
def detalle_venta_post_delete(sender, instance, **kwargs):
    """
    Señal que se ejecuta después de eliminar un detalle de venta.
    - Restaura el stock si la venta estaba completada
    """
    if instance.venta.estado == 'COMPLETADA' and not instance.producto.es_servicio:
        try:
            MovimientoStock.crear_movimiento(
                producto=instance.producto,
                tipo_movimiento='DEVOLUCION',
                cantidad=instance.cantidad,
                usuario=instance.venta.usuario,
                precio_unitario=instance.precio_unitario,
                referencia=f"Eliminación detalle venta #{instance.venta.numero_ticket}",
                observaciones="Stock restaurado por eliminación de detalle de venta"
            )
        except Exception:
            pass


""" S I G N A L S   P A R A   C O M P R A S """


@receiver(post_save, sender=Compra)
def compra_post_save(sender, instance, **kwargs):
    """
    Señal que se ejecuta después de guardar una compra.
    - Actualiza el stock cuando la compra cambia a estado RECIBIDA
    """
    if instance.estado == 'RECIBIDA' and not kwargs.get('created', False):
        # Verificar si realmente cambió a RECIBIDA
        if hasattr(instance, '_state') and instance._state.adding is False:
            # La lógica de crear movimientos ya está en el método marcar_como_recibida
            pass


@receiver(post_save, sender=DetalleCompra)
def detalle_compra_post_save(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta después de guardar un detalle de compra.
    - Actualiza el precio de compra del producto si es diferente
    """
    if instance.precio_unitario != instance.producto.precio_compra:
        # Actualizar precio de compra del producto
        Producto.objects.filter(id=instance.producto.id).update(
            precio_compra=instance.precio_unitario
        )

        # Si tiene margen configurado, recalcular precio de venta
        producto = instance.producto
        if producto.margen_ganancia > 0:
            nuevo_precio_venta = instance.precio_unitario * (1 + producto.margen_ganancia / 100)
            Producto.objects.filter(id=producto.id).update(precio_venta=nuevo_precio_venta)


""" S I G N A L S   P A R A   A L E R T A S   D E   S T O C K """


def generar_alerta_stock_producto(producto):
    """
    Función auxiliar para generar alertas de stock para un producto específico.
    """
    if producto.es_servicio or not producto.status:
        return

    # Eliminar alertas existentes para este producto
    AlertaStock.objects.filter(producto=producto).delete()

    # Crear nueva alerta según el estado del stock
    if producto.stock_actual == 0:
        AlertaStock.objects.create(
            producto=producto,
            tipo_alerta='SIN_STOCK',
            mensaje=f'El producto {producto.nombre} está agotado'
        )
    elif producto.requiere_reposicion:
        AlertaStock.objects.create(
            producto=producto,
            tipo_alerta='STOCK_BAJO',
            mensaje=f'El producto {producto.nombre} tiene stock bajo ({producto.stock_actual} unidades, mínimo: {producto.stock_minimo})'
        )
    elif producto.exceso_stock:
        AlertaStock.objects.create(
            producto=producto,
            tipo_alerta='EXCESO_STOCK',
            mensaje=f'El producto {producto.nombre} tiene exceso de stock ({producto.stock_actual} unidades, máximo: {producto.stock_maximo})'
        )


""" S I G N A L S   P A R A   L O G   D E   A C T I V I D A D E S """


@receiver(post_save, sender=Venta)
def log_venta_activity(sender, instance, created, **kwargs):
    """
    Señal para registrar actividad de ventas (opcional)
    """
    if created:
        # Aquí podrías agregar lógica para logging o auditoría
        pass


@receiver(post_save, sender=Compra)
def log_compra_activity(sender, instance, created, **kwargs):
    """
    Señal para registrar actividad de compras (opcional)
    """
    if created:
        # Aquí podrías agregar lógica para logging o auditoría
        pass


""" S I G N A L   P A R A   V A L I D A C I O N E S   A D I C I O N A L E S """


@receiver(pre_save, sender=DetalleVenta)
def validar_detalle_venta(sender, instance, **kwargs):
    """
    Validaciones adicionales antes de guardar un detalle de venta
    """
    # Validar que el precio de venta no sea menor al precio de compra (opcional)
    if instance.precio_unitario < instance.producto.precio_compra:
        # Podrías generar una alerta o warning aquí
        pass

    # Validar stock disponible
    if not instance.producto.es_servicio and instance.producto.stock_actual < instance.cantidad:
        from django.core.exceptions import ValidationError
        raise ValidationError(
            f'Stock insuficiente para {instance.producto.nombre}. '
            f'Disponible: {instance.producto.stock_actual}, Solicitado: {instance.cantidad}'
        )


""" A U T O - G E N E R A C I Ó N   D E   A L E R T A S """


@receiver(post_save, sender=Producto)
@receiver(post_save, sender=MovimientoStock)
def auto_generar_alertas_stock(sender, instance, **kwargs):
    """
    Auto-genera alertas de stock cuando es necesario
    """
    if sender == Producto:
        producto = instance
    elif sender == MovimientoStock:
        producto = instance.producto
    else:
        return

    # Usar transaction.on_commit para asegurar que se ejecute después del commit
    transaction.on_commit(lambda: generar_alerta_stock_producto(producto))


""" S I G N A L S   P A R A   L I M P I E Z A   D E   D A T O S """
@receiver(post_save, sender=AlertaStock)
def limpiar_alertas_duplicadas(sender, instance, created, **kwargs):
    """
    Limpia alertas duplicadas del mismo tipo para el mismo producto
    """
    if created:
        # Eliminar alertas duplicadas (mantener solo la más reciente)
        AlertaStock.objects.filter(
            producto=instance.producto,
            tipo_alerta=instance.tipo_alerta,
            status=True
        ).exclude(id=instance.id).delete()