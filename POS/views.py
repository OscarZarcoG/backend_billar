# POS/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, F, Count, Avg
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Categoria, Marca_Empresa, Proveedores, Producto, MovimientoStock,
    Compra, DetalleCompra, Venta, DetalleVenta, AlertaStock
)
from .serializers import (
    CategoriaSerializer, MarcaEmpresaSerializer, ProveedoresSerializer,
    ProductoListSerializer, ProductoDetailSerializer, ProductoCreateUpdateSerializer,
    MovimientoStockSerializer, MovimientoStockCreateSerializer,
    CompraListSerializer, CompraDetailSerializer, CompraCreateSerializer,
    VentaListSerializer, VentaDetailSerializer, VentaCreateSerializer,
    AlertaStockSerializer, ProductoStockSerializer, ProductoVentasSerializer,
    CategoriaSimpleSerializer, MarcaEmpresaSimpleSerializer, ProveedorSimpleSerializer,
    ProductoSimpleSerializer
)

""" P A G I N A T I O N """
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


""" C A T E G O R I A S   V I E W S E T """
class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']

    def get_queryset(self):
        return Categoria.objects.filter(status=True)

    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        queryset = self.get_queryset()
        serializer = CategoriaSimpleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        categoria = self.get_object()
        categoria.soft_delete()
        return Response({'message': 'Categoría eliminada correctamente'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        categoria = self.get_object()
        categoria.restore()
        return Response({'message': 'Categoría restaurada correctamente'})


""" M A R C A S   E M P R E S A S   V I E W S E T """
class MarcaEmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = MarcaEmpresaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'sitio_web']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']

    def get_queryset(self):
        return Marca_Empresa.objects.filter(status=True)

    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        queryset = self.get_queryset()
        serializer = MarcaEmpresaSimpleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        marca = self.get_object()
        marca.soft_delete()
        return Response({'message': 'Marca eliminada correctamente'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        marca = self.get_object()
        marca.restore()
        return Response({'message': 'Marca restaurada correctamente'})


""" P R O V E E D O R E S   V I E W S E T """
class ProveedoresViewSet(viewsets.ModelViewSet):
    serializer_class = ProveedoresSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa']
    search_fields = ['nombre', 'telefono', 'email']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']

    def get_queryset(self):
        return Proveedores.objects.filter(status=True).select_related('empresa')

    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        """Lista simple para selects"""
        queryset = self.get_queryset()
        serializer = ProveedorSimpleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        proveedor = self.get_object()
        proveedor.soft_delete()
        return Response({'message': 'Proveedor eliminado correctamente'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        proveedor = self.get_object()
        proveedor.restore()
        return Response({'message': 'Proveedor restaurado correctamente'})


""" P R O D U C T O S   V I E W S E T """
class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['marca', 'categoria', 'proveedor_principal', 'es_servicio']
    search_fields = ['nombre', 'codigo_barras', 'sku', 'descripcion']
    ordering_fields = ['nombre', 'precio_venta', 'stock_actual', 'created_at']
    ordering = ['nombre']

    def get_queryset(self):
        return Producto.objects.filter(status=True).select_related(
            'marca', 'categoria', 'proveedor_principal'
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductoCreateUpdateSerializer
        else:
            return ProductoDetailSerializer

    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        """Lista simple para selects"""
        queryset = self.get_queryset()
        serializer = ProductoSimpleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def buscar_por_codigo(self, request):
        codigo = request.query_params.get('codigo', '')
        if not codigo:
            return Response({'error': 'Código requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            producto = Producto.objects.get(codigo_barras=codigo, status=True)
            serializer = ProductoDetailSerializer(producto)
            return Response(serializer.data)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        productos = self.get_queryset().filter(
            stock_actual__lte=F('stock_minimo'),
            es_servicio=False
        )
        serializer = ProductoStockSerializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sin_stock(self, request):
        productos = self.get_queryset().filter(stock_actual=0, es_servicio=False)
        serializer = ProductoStockSerializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def exceso_stock(self, request):
        productos = self.get_queryset().filter(
            stock_actual__gt=F('stock_maximo'),
            es_servicio=False
        )
        serializer = ProductoStockSerializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def actualizar_precio_por_margen(self, request, pk=None):
        producto = self.get_object()
        producto.actualizar_precio_venta_por_margen()
        producto.save()
        serializer = self.get_serializer(producto)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        producto = self.get_object()
        producto.soft_delete()
        return Response({'message': 'Producto eliminado correctamente'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        producto = self.get_object()
        producto.restore()
        return Response({'message': 'Producto restaurado correctamente'})


""" M O V I M I E N T O S   S T O C K   V I E W S E T """
class MovimientoStockViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoStockSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'tipo_movimiento', 'usuario']
    search_fields = ['producto__nombre', 'referencia', 'observaciones']
    ordering_fields = ['fecha']
    ordering = ['-fecha']

    def get_queryset(self):
        return MovimientoStock.objects.filter(status=True).select_related(
            'producto', 'usuario'
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return MovimientoStockCreateSerializer
        return MovimientoStockSerializer

    @action(detail=False, methods=['get'])
    def por_producto(self, request):
        """Movimientos de un producto específico"""
        producto_id = request.query_params.get('producto_id')
        if not producto_id:
            return Response({'error': 'producto_id requerido'}, status=status.HTTP_400_BAD_REQUEST)

        movimientos = self.get_queryset().filter(producto_id=producto_id)
        page = self.paginate_queryset(movimientos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(movimientos, many=True)
        return Response(serializer.data)


""" C O M P R A S   V I E W S E T """
class CompraViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['proveedor', 'estado', 'usuario']
    search_fields = ['numero_factura', 'proveedor__nombre']
    ordering_fields = ['fecha_pedido', 'total']
    ordering = ['-fecha_pedido']

    def get_queryset(self):
        return Compra.objects.filter(status=True).select_related('proveedor', 'usuario')

    def get_serializer_class(self):
        if self.action == 'list':
            return CompraListSerializer
        elif self.action == 'create':
            return CompraCreateSerializer
        else:
            return CompraDetailSerializer

    @action(detail=True, methods=['post'])
    def marcar_recibida(self, request, pk=None):
        compra = self.get_object()
        if compra.estado == 'RECIBIDA':
            return Response({'error': 'La compra ya está marcada como recibida'},
                            status=status.HTTP_400_BAD_REQUEST)

        compra.marcar_como_recibida()
        serializer = self.get_serializer(compra)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        compra = self.get_object()
        if compra.estado == 'RECIBIDA':
            return Response({'error': 'No se puede cancelar una compra ya recibida'},
                            status=status.HTTP_400_BAD_REQUEST)

        compra.estado = 'CANCELADA'
        compra.save()
        return Response({'message': 'Compra cancelada correctamente'})

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        compras = self.get_queryset().filter(estado='PENDIENTE')
        page = self.paginate_queryset(compras)
        if page is not None:
            serializer = CompraListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompraListSerializer(compras, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        compra = self.get_object()
        if compra.estado == 'RECIBIDA':
            return Response({'error': 'No se puede eliminar una compra recibida'},
                            status=status.HTTP_400_BAD_REQUEST)
        compra.soft_delete()
        return Response({'message': 'Compra eliminada correctamente'})


""" V E N T A S   V I E W S E T """
class VentaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['usuario', 'cliente', 'metodo_pago', 'estado']
    search_fields = ['numero_ticket', 'cliente__nombre']
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']

    def get_queryset(self):
        return Venta.objects.filter(status=True).select_related('usuario', 'cliente')

    def get_serializer_class(self):
        if self.action == 'list':
            return VentaListSerializer
        elif self.action == 'create':
            return VentaCreateSerializer
        else:
            return VentaDetailSerializer

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        venta = self.get_object()
        if venta.estado in ['CANCELADA', 'DEVUELTA']:
            return Response({'error': 'La venta ya está cancelada o devuelta'},
                            status=status.HTTP_400_BAD_REQUEST)

        for detalle in venta.detalles.all():
            if not detalle.producto.es_servicio:
                MovimientoStock.crear_movimiento(
                    producto=detalle.producto,
                    tipo_movimiento='DEVOLUCION',
                    cantidad=detalle.cantidad,
                    usuario=request.user,
                    precio_unitario=detalle.precio_unitario,
                    referencia=f"Cancelación Venta #{venta.numero_ticket}"
                )

        venta.estado = 'CANCELADA'
        venta.save()
        return Response({'message': 'Venta cancelada correctamente'})

    @action(detail=False, methods=['get'])
    def ventas_hoy(self, request):
        """Ventas del día actual"""
        hoy = timezone.now().date()
        ventas = self.get_queryset().filter(fecha__date=hoy, estado='COMPLETADA')

        # Estadísticas del día
        stats = ventas.aggregate(
            total_ventas=Count('id'),
            total_ingresos=Coalesce(Sum('detalles__cantidad'), Decimal('0.00')),
            total_ganancia=Coalesce(
                Sum((F('detalles__precio_unitario') - F('detalles__producto__precio_compra')) *
                    F('detalles__cantidad')), Decimal('0.00')
            )
        )

        page = self.paginate_queryset(ventas)
        if page is not None:
            serializer = VentaListSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['estadisticas'] = stats
            return Response(response_data)

        serializer = VentaListSerializer(ventas, many=True)
        return Response({
            'results': serializer.data,
            'estadisticas': stats
        })

    @action(detail=False, methods=['get'])
    def reporte_periodo(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return Response({'error': 'fecha_inicio y fecha_fin son requeridas'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Formato de fecha inválido (YYYY-MM-DD)'},
                            status=status.HTTP_400_BAD_REQUEST)

        ventas = self.get_queryset().filter(
            fecha__date__range=[fecha_inicio, fecha_fin],
            estado='COMPLETADA'
        )

        stats = ventas.aggregate(
            total_ventas=Count('id'),
            total_ingresos=Coalesce(Sum(F('detalles__cantidad') * F('detalles__precio_unitario')),
                                    Decimal('0.00')),
            total_ganancia=Coalesce(
                Sum((F('detalles__precio_unitario') - F('detalles__producto__precio_compra')) *
                    F('detalles__cantidad')), Decimal('0.00')
            ),
            ticket_promedio=Avg(F('detalles__cantidad') * F('detalles__precio_unitario'))
        )

        return Response({
            'periodo': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'estadisticas': stats
        })

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        venta = self.get_object()
        if venta.estado == 'COMPLETADA':
            return Response({'error': 'No se puede eliminar una venta completada'},
                            status=status.HTTP_400_BAD_REQUEST)
        venta.soft_delete()
        return Response({'message': 'Venta eliminada correctamente'})


""" A L E R T A S   S T O C K   V I E W S E T """
class AlertaStockViewSet(viewsets.ModelViewSet):
    serializer_class = AlertaStockSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_alerta', 'leida', 'usuario_asignado']
    search_fields = ['producto__nombre', 'mensaje']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return AlertaStock.objects.filter(status=True).select_related('producto', 'usuario_asignado')

    @action(detail=False, methods=['post'])
    def generar_alertas(self, request):
        AlertaStock.generar_alertas_stock()
        return Response({'message': 'Alertas generadas correctamente'})

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """Marcar alerta como leída"""
        alerta = self.get_object()
        alerta.leida = True
        alerta.save()
        return Response({'message': 'Alerta marcada como leída'})

    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        AlertaStock.objects.filter(leida=False, status=True).update(leida=True)
        return Response({'message': 'Todas las alertas marcadas como leídas'})

    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        alertas = self.get_queryset().filter(leida=False)
        page = self.paginate_queryset(alertas)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(alertas, many=True)
        return Response(serializer.data)


""" R E P O R T E S   Y   E S T A D I S T I C A S """
from rest_framework.views import APIView


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoy = timezone.now().date()
        mes_actual = timezone.now().replace(day=1).date()

        ventas_hoy = Venta.objects.filter(fecha__date=hoy, estado='COMPLETADA')
        stats_hoy = ventas_hoy.aggregate(
            total_ventas=Count('id'),
            total_ingresos=Coalesce(
                Sum(F('detalles__cantidad') * F('detalles__precio_unitario')),
                Decimal('0.00')
            )
        )

        ventas_mes = Venta.objects.filter(fecha__date__gte=mes_actual, estado='COMPLETADA')
        stats_mes = ventas_mes.aggregate(
            total_ventas=Count('id'),
            total_ingresos=Coalesce(
                Sum(F('detalles__cantidad') * F('detalles__precio_unitario')),
                Decimal('0.00')
            )
        )

        productos_sin_stock = Producto.objects.filter(
            stock_actual=0, es_servicio=False, status=True
        ).count()

        productos_stock_bajo = Producto.objects.filter(
            stock_actual__lte=F('stock_minimo'),
            stock_actual__gt=0,
            es_servicio=False,
            status=True
        ).count()

        alertas_sin_leer = AlertaStock.objects.filter(leida=False, status=True).count()

        compras_pendientes = Compra.objects.filter(estado='PENDIENTE', status=True).count()

        return Response({
            'ventas_hoy': stats_hoy,
            'ventas_mes': stats_mes,
            'stock': {
                'productos_sin_stock': productos_sin_stock,
                'productos_stock_bajo': productos_stock_bajo,
            },
            'alertas_sin_leer': alertas_sin_leer,
            'compras_pendientes': compras_pendientes,
        })


class ProductosMasVendidosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dias = int(request.query_params.get('dias', 30))
        fecha_limite = timezone.now().date() - timedelta(days=dias)

        productos = Producto.objects.filter(
            detalles_venta__venta__fecha__date__gte=fecha_limite,
            detalles_venta__venta__estado='COMPLETADA',
            status=True
        ).annotate(
            total_vendido=Sum('detalles_venta__cantidad'),
            ingresos_totales=Sum(
                F('detalles_venta__cantidad') * F('detalles_venta__precio_unitario')
            ),
            ganancia_total=Sum(
                (F('detalles_venta__precio_unitario') - F('precio_compra')) *
                F('detalles_venta__cantidad')
            )
        ).order_by('-total_vendido')[:10]

        serializer = ProductoVentasSerializer(productos, many=True)
        return Response(serializer.data)