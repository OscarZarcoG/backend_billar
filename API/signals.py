from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import (
    Producto, MovimientoStock, Alquiler, Consumo,
    VentaDirecta, DetalleVenta, Compra, DetalleCompra,
    Notificacion, EstadisticasDiarias
)
from django.utils import timezone
from datetime import timedelta


@receiver(post_save, sender=MovimientoStock)
def actualizar_stock(sender, instance, created, **kwargs):
    if created:
        if instance.tipo == 'IN':
            instance.producto.stock_actual += instance.cantidad
        elif instance.tipo == 'SA':
            instance.producto.stock_actual -= instance.cantidad
        instance.producto.save()


@receiver(post_save, sender=Alquiler)
def manejar_estado_mesa(sender, instance, created, **kwargs):
    if created and instance.estado == 'AC':
        instance.mesa.estado = 'OC'
        instance.mesa.save()
    elif instance.estado in ['FI', 'CA']:
        instance.mesa.estado = 'LI'
        instance.mesa.save()


@receiver(post_save, sender=Consumo)
def crear_movimiento_stock_consumo(sender, instance, created, **kwargs):
    if created:
        MovimientoStock.objects.create(
            producto=instance.producto,
            tipo='SA',
            cantidad=instance.cantidad,
            motivo=f"Consumo en alquiler #{instance.alquiler.id}",
            usuario=instance.usuario
        )


@receiver(post_save, sender=DetalleVenta)
def crear_movimiento_stock_venta(sender, instance, created, **kwargs):
    if created:
        MovimientoStock.objects.create(
            producto=instance.producto,
            tipo='SA',
            cantidad=instance.cantidad,
            motivo=f"Venta directa #{instance.venta.id}",
            usuario=instance.venta.usuario
        )


@receiver(post_save, sender=DetalleCompra)
def crear_movimiento_stock_compra(sender, instance, created, **kwargs):
    if created and instance.compra.estado == 'RE':
        MovimientoStock.objects.create(
            producto=instance.producto,
            tipo='IN',
            cantidad=instance.cantidad,
            motivo=f"Compra #{instance.compra.id}",
            usuario=instance.compra.usuario
        )


@receiver(post_save, sender=Producto)
def notificar_stock_bajo(sender, instance, **kwargs):
    if instance.stock_actual <= instance.stock_minimo:
        usuarios = User.objects.filter(is_staff=True)
        for usuario in usuarios:
            Notificacion.objects.create(
                usuario=usuario,
                tipo='AL',
                titulo=f"Stock bajo: {instance.nombre}",
                mensaje=f"El producto {instance.nombre} tiene stock bajo ({instance.stock_actual} unidades).",
                enlace=f"/productos/{instance.id}"
            )


@receiver(post_save, sender=Alquiler)
def actualizar_estadisticas_alquiler(sender, instance, **kwargs):
    if instance.estado == 'FI':
        fecha = instance.tiempo_inicio.date()
        estadistica, created = EstadisticasDiarias.objects.get_or_create(fecha=fecha)

        estadistica.numero_alquileres += 1
        estadistica.ventas_alquiler += instance.monto_total
        estadistica.ventas_totales += instance.monto_total
        estadistica.tiempo_total_alquiler += instance.tiempo_transcurrido
        estadistica.save()


@receiver(post_save, sender=VentaDirecta)
def actualizar_estadisticas_venta(sender, instance, **kwargs):
    if instance.estado == 'CO':
        fecha = instance.fecha_hora.date()
        estadistica, created = EstadisticasDiarias.objects.get_or_create(fecha=fecha)

        estadistica.numero_ventas += 1
        estadistica.ventas_productos += instance.rpice_total
        estadistica.ventas_totales += instance.rpice_total
        estadistica.save()