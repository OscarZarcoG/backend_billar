# POS/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import (
    Categoria, Marca_Empresa, Proveedores, Producto, MovimientoStock,
    Compra, DetalleCompra, Venta, DetalleVenta, AlertaStock
)
from clientesAPI.serializers import ClienteSerializer

""" U S E R   S E R I A L I Z E R """
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


""" C A T E G O R I A   S E R I A L I Z E R """
class CategoriaSerializer(serializers.ModelSerializer):
    productos_count = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'status', 'created_at', 'updated_at', 'productos_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_productos_count(self, obj):
        return obj.productos.filter(status=True).count()


""" M A R C A   E M P R E S A   S E R I A L I Z E R """
class MarcaEmpresaSerializer(serializers.ModelSerializer):
    productos_count = serializers.SerializerMethodField()
    proveedores_count = serializers.SerializerMethodField()

    class Meta:
        model = Marca_Empresa
        fields = [
            'id', 'nombre', 'logo', 'sitio_web', 'telefono', 'status',
            'created_at', 'updated_at', 'productos_count', 'proveedores_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_productos_count(self, obj):
        return obj.productos.filter(status=True).count()

    def get_proveedores_count(self, obj):
        return obj.proveedores.filter(status=True).count()


""" P R O V E E D O R E S   S E R I A L I Z E R """
class ProveedoresSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    empresa_data = MarcaEmpresaSerializer(source='empresa', read_only=True)
    productos_suministrados_count = serializers.SerializerMethodField()

    class Meta:
        model = Proveedores
        fields = [
            'id', 'nombre', 'empresa', 'empresa_nombre', 'empresa_data',
            'telefono', 'email', 'direccion', 'status', 'created_at',
            'updated_at', 'productos_suministrados_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_productos_suministrados_count(self, obj):
        return obj.productos_suministrados.filter(status=True).count()


""" P R O D U C T O   S E R I A L I Z E R S """
class ProductoListSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor_principal.nombre', read_only=True)
    ganancia_absoluta = serializers.ReadOnlyField()
    ganancia_porcentual = serializers.ReadOnlyField()
    disponible = serializers.ReadOnlyField()
    requiere_reposicion = serializers.ReadOnlyField()
    exceso_stock = serializers.ReadOnlyField()
    precio_con_impuesto = serializers.ReadOnlyField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'codigo_barras', 'sku', 'marca', 'marca_nombre',
            'categoria', 'categoria_nombre', 'precio_compra', 'precio_venta',
            'margen_ganancia', 'stock_actual', 'stock_minimo', 'stock_maximo',
            'proveedor_principal', 'proveedor_nombre', 'imagen', 'es_servicio',
            'impuesto', 'status', 'ganancia_absoluta', 'ganancia_porcentual',
            'disponible', 'requiere_reposicion', 'exceso_stock', 'precio_con_impuesto'
        ]


class ProductoDetailSerializer(serializers.ModelSerializer):
    marca_data = MarcaEmpresaSerializer(source='marca', read_only=True)
    categoria_data = CategoriaSerializer(source='categoria', read_only=True)
    proveedor_data = ProveedoresSerializer(source='proveedor_principal', read_only=True)
    ganancia_absoluta = serializers.ReadOnlyField()
    ganancia_porcentual = serializers.ReadOnlyField()
    disponible = serializers.ReadOnlyField()
    requiere_reposicion = serializers.ReadOnlyField()
    exceso_stock = serializers.ReadOnlyField()
    precio_con_impuesto = serializers.ReadOnlyField()
    movimientos_recientes = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'codigo_barras', 'sku', 'marca', 'marca_data',
            'categoria', 'categoria_data', 'descripcion', 'precio_compra',
            'precio_venta', 'margen_ganancia', 'proveedor_principal', 'proveedor_data',
            'imagen', 'stock_actual', 'stock_minimo', 'stock_maximo', 'peso',
            'dimensiones', 'es_servicio', 'impuesto', 'status', 'created_at',
            'updated_at', 'ganancia_absoluta', 'ganancia_porcentual', 'disponible',
            'requiere_reposicion', 'exceso_stock', 'precio_con_impuesto', 'movimientos_recientes'
        ]
        read_only_fields = ['created_at', 'updated_at', 'sku']

    def get_movimientos_recientes(self, obj):
        movimientos = obj.movimientos.all()[:10]
        return MovimientoStockSerializer(movimientos, many=True).data

    def validate(self, data):
        if data.get('precio_venta', 0) < data.get('precio_compra', 0):
            raise serializers.ValidationError(
                {'precio_venta': 'El precio de venta no puede ser menor al precio de compra'}
            )
        if data.get('stock_maximo', 0) < data.get('stock_minimo', 0):
            raise serializers.ValidationError(
                {'stock_maximo': 'El stock máximo debe ser mayor al stock mínimo'}
            )
        return data

    def update(self, instance, validated_data):
        if 'margen_ganancia' in validated_data and validated_data['margen_ganancia'] > 0:
            validated_data['precio_venta'] = instance.precio_compra * (
                    1 + validated_data['margen_ganancia'] / 100
            )
        return super().update(instance, validated_data)


class ProductoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'codigo_barras', 'marca', 'categoria', 'descripcion',
            'precio_compra', 'precio_venta', 'margen_ganancia', 'proveedor_principal',
            'imagen', 'stock_actual', 'stock_minimo', 'stock_maximo', 'peso',
            'dimensiones', 'es_servicio', 'impuesto'
        ]

    def validate_codigo_barras(self, value):
        instance = getattr(self, 'instance', None)
        if Producto.objects.filter(codigo_barras=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe un producto con este código de barras.")
        return value


""" M O V I M I E N T O   S T O C K   S E R I A L I Z E R """
class MovimientoStockSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    tipo_movimiento_display = serializers.CharField(source='get_tipo_movimiento_display', read_only=True)

    class Meta:
        model = MovimientoStock
        fields = [
            'id', 'producto', 'producto_nombre', 'tipo_movimiento', 'tipo_movimiento_display',
            'cantidad', 'stock_anterior', 'stock_nuevo', 'fecha', 'usuario',
            'usuario_nombre', 'precio_unitario', 'referencia', 'observaciones'
        ]
        read_only_fields = ['stock_anterior', 'stock_nuevo', 'fecha']


class MovimientoStockCreateSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.filter(status=True))
    tipo_movimiento = serializers.ChoiceField(choices=MovimientoStock.TIPO_MOVIMIENTO)
    cantidad = serializers.IntegerField(min_value=1)
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    referencia = serializers.CharField(max_length=100, required=False, allow_blank=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        usuario = self.context['request'].user
        return MovimientoStock.crear_movimiento(
            usuario=usuario,
            **validated_data
        )


""" C O M P R A   S E R I A L I Z E R S """
class DetalleCompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo_barras', read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetalleCompra
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_codigo',
            'cantidad', 'precio_unitario', 'subtotal'
        ]

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value


class CompraListSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    subtotal = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    cantidad_items = serializers.ReadOnlyField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Compra
        fields = [
            'id', 'numero_factura', 'proveedor', 'proveedor_nombre',
            'usuario', 'usuario_nombre', 'fecha_pedido', 'fecha_recepcion',
            'estado', 'estado_display', 'descuento', 'impuesto',
            'subtotal', 'total', 'cantidad_items'
        ]


class CompraDetailSerializer(serializers.ModelSerializer):
    proveedor_data = ProveedoresSerializer(source='proveedor', read_only=True)
    usuario_data = UserSerializer(source='usuario', read_only=True)
    detalles = DetalleCompraSerializer(many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    cantidad_items = serializers.ReadOnlyField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Compra
        fields = [
            'id', 'numero_factura', 'proveedor', 'proveedor_data',
            'usuario', 'usuario_data', 'fecha_pedido', 'fecha_recepcion',
            'estado', 'estado_display', 'observaciones', 'descuento',
            'impuesto', 'detalles', 'subtotal', 'total', 'cantidad_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'fecha_pedido']


class CompraCreateSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)

    class Meta:
        model = Compra
        fields = [
            'numero_factura', 'proveedor', 'observaciones',
            'descuento', 'impuesto', 'detalles'
        ]

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un detalle de compra")
        return value

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        usuario = self.context['request'].user

        compra = Compra.objects.create(usuario=usuario, **validated_data)

        for detalle_data in detalles_data:
            DetalleCompra.objects.create(compra=compra, **detalle_data)

        return compra


""" V E N T A   S E R I A L I Z E R S """
class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo_barras', read_only=True)
    precio_con_descuento = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    ganancia = serializers.ReadOnlyField()

    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_codigo',
            'cantidad', 'precio_unitario', 'descuento_unitario',
            'precio_con_descuento', 'subtotal', 'ganancia'
        ]

    def validate(self, data):
        producto = data.get('producto')
        cantidad = data.get('cantidad', 1)

        if producto and not producto.es_servicio:
            if cantidad > producto.stock_actual:
                raise serializers.ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {producto.stock_actual}'
                })

        precio_unitario = data.get('precio_unitario', 0)
        descuento_unitario = data.get('descuento_unitario', 0)

        if descuento_unitario > precio_unitario:
            raise serializers.ValidationError({
                'descuento_unitario': 'El descuento no puede ser mayor al precio unitario'
            })

        return data


class VentaListSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    subtotal = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    ganancia = serializers.ReadOnlyField()
    cantidad_items = serializers.ReadOnlyField()
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Venta
        fields = [
            'id', 'numero_ticket', 'usuario', 'usuario_nombre', 'fecha',
            'cliente', 'cliente_nombre', 'metodo_pago', 'metodo_pago_display',
            'estado', 'estado_display', 'descuento', 'impuesto',
            'subtotal', 'total', 'ganancia', 'cantidad_items'
        ]


class VentaDetailSerializer(serializers.ModelSerializer):
    usuario_data = UserSerializer(source='usuario', read_only=True)
    cliente_data = ClienteSerializer(source='cliente', read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    ganancia = serializers.ReadOnlyField()
    cantidad_items = serializers.ReadOnlyField()
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Venta
        fields = [
            'id', 'numero_ticket', 'usuario', 'usuario_data', 'fecha',
            'cliente', 'cliente_data', 'metodo_pago', 'metodo_pago_display',
            'estado', 'estado_display', 'descuento', 'impuesto', 'observaciones',
            'detalles', 'subtotal', 'total', 'ganancia', 'cantidad_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'numero_ticket', 'fecha']


class VentaCreateSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Venta
        fields = [
            'cliente', 'metodo_pago', 'descuento', 'impuesto',
            'observaciones', 'detalles'
        ]

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un detalle de venta")
        return value

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        usuario = self.context['request'].user

        venta = Venta.objects.create(usuario=usuario, **validated_data)

        for detalle_data in detalles_data:
            DetalleVenta.objects.create(venta=venta, **detalle_data)

        return venta


""" A L E R T A   S T O C K   S E R I A L I Z E R """
class AlertaStockSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo_barras', read_only=True)
    producto_stock = serializers.IntegerField(source='producto.stock_actual', read_only=True)
    usuario_asignado_nombre = serializers.CharField(source='usuario_asignado.get_full_name', read_only=True)
    tipo_alerta_display = serializers.CharField(source='get_tipo_alerta_display', read_only=True)

    class Meta:
        model = AlertaStock
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_codigo', 'producto_stock',
            'tipo_alerta', 'tipo_alerta_display', 'mensaje', 'leida',
            'usuario_asignado', 'usuario_asignado_nombre', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


""" S E R I A L I Z E R S   P A R A   R E P O R T E S """
class ProductoStockSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    disponible = serializers.ReadOnlyField()
    requiere_reposicion = serializers.ReadOnlyField()
    exceso_stock = serializers.ReadOnlyField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'codigo_barras', 'marca_nombre', 'categoria_nombre',
            'stock_actual', 'stock_minimo', 'stock_maximo', 'disponible',
            'requiere_reposicion', 'exceso_stock', 'es_servicio'
        ]


class ProductoVentasSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    total_vendido = serializers.IntegerField(read_only=True)
    ingresos_totales = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    ganancia_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'codigo_barras', 'marca_nombre', 'categoria_nombre',
            'precio_venta', 'precio_compra', 'total_vendido',
            'ingresos_totales', 'ganancia_total'
        ]


""" S E R I A L I Z E R S   S I M P L E S   P A R A   S E L E C T S """
class CategoriaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class MarcaEmpresaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca_Empresa
        fields = ['id', 'nombre']


class ProveedorSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedores
        fields = ['id', 'nombre']


class ProductoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'codigo_barras', 'precio_venta', 'stock_actual', 'disponible']