from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import (
    Cliente, Categoria, Producto, MovimientoStock, TipoMesa, Mesa,
    MetodoPago, CierreCaja, Alquiler, Consumo, TransferenciaAlquiler,
    Pago, VentaDirecta, DetalleVenta, Proveedor, Compra, DetalleCompra,
    Notificacion, Configuracion, EstadisticasDiarias
)
from .serializers import (
    ClienteSerializer, CategoriaSerializer, ProductoSerializer,
    MovimientoStockSerializer, TipoMesaSerializer, MesaSerializer,
    MetodoPagoSerializer, CierreCajaSerializer, AlquilerSerializer,
    ConsumoSerializer, TransferenciaAlquilerSerializer, PagoSerializer,
    VentaDirectaSerializer, DetalleVentaSerializer, ProveedorSerializer,
    CompraSerializer, DetalleCompraSerializer, NotificacionSerializer,
    ConfiguracionSerializer, EstadisticasDiariasSerializer
)
from .exceptions import (
    PasswordMismatch, PasswordRequired
)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    @action(detail=False, methods=['get'])
    def frecuentes(self, request):
        frecuentes = Cliente.objects.filter(tipo_frecuencia='FR')
        serializer = self.get_serializer(frecuentes, many=True)
        return Response(serializer.data)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        productos = Producto.objects.filter(stock_actual__lte=models.F('stock_minimo'))
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)


class MovimientoStockViewSet(viewsets.ModelViewSet):
    queryset = MovimientoStock.objects.all()
    serializer_class = MovimientoStockSerializer


class TipoMesaViewSet(viewsets.ModelViewSet):
    queryset = TipoMesa.objects.all()
    serializer_class = TipoMesaSerializer


class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        disponibles = Mesa.objects.filter(estado='LI', activo=True)
        serializer = self.get_serializer(disponibles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        mesa = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in dict(Mesa.OPCIONES_ESTADO).keys():
            return Response(
                {'error': 'Estado no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        mesa.estado = nuevo_estado
        mesa.save()
        return Response({'status': 'Estado actualizado'})


class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer


class CierreCajaViewSet(viewsets.ModelViewSet):
    queryset = CierreCaja.objects.all()
    serializer_class = CierreCajaSerializer

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        cierre = self.get_object()
        if cierre.esta_cerrada:
            return Response(
                {'error': 'La caja ya está cerrada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        monto_final = request.data.get('monto_final')
        observaciones = request.data.get('observaciones', '')
        usuario_cierre = request.user

        cierre.fecha_cierre = timezone.now()
        cierre.monto_final = monto_final
        cierre.ventas_totales = cierre.calcular_ventas_totales
        cierre.diferencia = float(monto_final) - float(cierre.monto_inicial) - float(cierre.ventas_totales)
        cierre.usuario_cierre = usuario_cierre
        cierre.observaciones = observaciones
        cierre.save()

        serializer = self.get_serializer(cierre)
        return Response(serializer.data)


class AlquilerViewSet(viewsets.ModelViewSet):
    queryset = Alquiler.objects.all()
    serializer_class = AlquilerSerializer

    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        alquiler = self.get_object()
        if alquiler.estado != 'AC':
            return Response(
                {'error': 'El alquiler no está activo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        alquiler.estado = 'FI'
        alquiler.tiempo_finalizacion = timezone.now()
        alquiler.save(update_fields=['estado', 'tiempo_finalizacion'])

        serializer = self.get_serializer(alquiler)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def consumos(self, request, pk=None):
        alquiler = self.get_object()
        consumos = alquiler.consumos.all()
        serializer = ConsumoSerializer(consumos, many=True)
        return Response(serializer.data)


class ConsumoViewSet(viewsets.ModelViewSet):
    queryset = Consumo.objects.all()
    serializer_class = ConsumoSerializer


class TransferenciaAlquilerViewSet(viewsets.ModelViewSet):
    queryset = TransferenciaAlquiler.objects.all()
    serializer_class = TransferenciaAlquilerSerializer


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer


class VentaDirectaViewSet(viewsets.ModelViewSet):
    queryset = VentaDirecta.objects.all()
    serializer_class = VentaDirectaSerializer

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        venta = self.get_object()
        detalles = venta.detalles.all()
        serializer = DetalleVentaSerializer(detalles, many=True)
        return Response(serializer.data)


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        compra = self.get_object()
        detalles = compra.detalles.all()
        serializer = DetalleCompraSerializer(detalles, many=True)
        return Response(serializer.data)


class DetalleCompraViewSet(viewsets.ModelViewSet):
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.estado = 'LE'
        notificacion.fecha_lectura = timezone.now()
        notificacion.save()
        return Response({'status': 'Notificación marcada como leída'})


class ConfiguracionViewSet(viewsets.ModelViewSet):
    queryset = Configuracion.objects.all()
    serializer_class = ConfiguracionSerializer


class EstadisticasDiariasViewSet(viewsets.ModelViewSet):
    queryset = EstadisticasDiarias.objects.all()
    serializer_class = EstadisticasDiariasSerializer

    @action(detail=False, methods=['get'])
    def hoy(self, request):
        hoy = timezone.now().date()
        estadistica, created = EstadisticasDiarias.objects.get_or_create(fecha=hoy)
        serializer = self.get_serializer(estadistica)
        return Response(serializer.data)