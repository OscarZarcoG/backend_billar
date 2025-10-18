from rest_framework import serializers
from .models import (
    Cliente, Categoria, Producto, MovimientoStock, TipoMesa, Mesa,
    MetodoPago, CierreCaja, Alquiler, Consumo, TransferenciaAlquiler,
    Pago, VentaDirecta, DetalleVenta, Proveedor, Compra, DetalleCompra,
    Notificacion, Configuracion, EstadisticasDiarias
)


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )

    class Meta:
        model = Producto
        fields = '__all__'


class MovimientoStockSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )
    usuario = serializers.StringRelatedField()

    class Meta:
        model = MovimientoStock
        fields = '__all__'
        read_only_fields = ('created_at',)


class TipoMesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMesa
        fields = '__all__'


class MesaSerializer(serializers.ModelSerializer):
    tipo = TipoMesaSerializer(read_only=True)
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoMesa.objects.all(), source='tipo', write_only=True
    )

    class Meta:
        model = Mesa
        fields = '__all__'


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'


class CierreCajaSerializer(serializers.ModelSerializer):
    usuario_apertura = serializers.StringRelatedField()
    usuario_cierre = serializers.StringRelatedField()

    class Meta:
        model = CierreCaja
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AlquilerSerializer(serializers.ModelSerializer):
    mesa = MesaSerializer(read_only=True)
    mesa_id = serializers.PrimaryKeyRelatedField(
        queryset=Mesa.objects.all(), source='mesa', write_only=True
    )
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True, allow_null=True
    )
    usuario = serializers.StringRelatedField()
    cierre_caja = CierreCajaSerializer(read_only=True)
    cierre_caja_id = serializers.PrimaryKeyRelatedField(
        queryset=CierreCaja.objects.all(), source='cierre_caja', write_only=True, allow_null=True
    )

    class Meta:
        model = Alquiler
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ConsumoSerializer(serializers.ModelSerializer):
    alquiler = AlquilerSerializer(read_only=True)
    alquiler_id = serializers.PrimaryKeyRelatedField(
        queryset=Alquiler.objects.all(), source='alquiler', write_only=True
    )
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Consumo
        fields = '__all__'
        read_only_fields = ('created_at', 'subtotal')


class TransferenciaAlquilerSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()
    alquiler_origen = AlquilerSerializer(read_only=True)
    alquiler_origen_id = serializers.PrimaryKeyRelatedField(
        queryset=Alquiler.objects.all(), source='alquiler_origen', write_only=True
    )
    alquiler_destino = AlquilerSerializer(read_only=True)
    alquiler_destino_id = serializers.PrimaryKeyRelatedField(
        queryset=Alquiler.objects.all(), source='alquiler_destino', write_only=True
    )
    mesa_origen = MesaSerializer(read_only=True)
    mesa_origen_id = serializers.PrimaryKeyRelatedField(
        queryset=Mesa.objects.all(), source='mesa_origen', write_only=True
    )
    mesa_destino = MesaSerializer(read_only=True)
    mesa_destino_id = serializers.PrimaryKeyRelatedField(
        queryset=Mesa.objects.all(), source='mesa_destino', write_only=True
    )

    class Meta:
        model = TransferenciaAlquiler
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PagoSerializer(serializers.ModelSerializer):
    alquiler = AlquilerSerializer(read_only=True)
    alquiler_id = serializers.PrimaryKeyRelatedField(
        queryset=Alquiler.objects.all(), source='alquiler', write_only=True
    )
    metodo_pago = MetodoPagoSerializer(read_only=True)
    metodo_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=MetodoPago.objects.all(), source='metodo_pago', write_only=True
    )
    usuario = serializers.StringRelatedField()
    cierre_caja = CierreCajaSerializer(read_only=True)
    cierre_caja_id = serializers.PrimaryKeyRelatedField(
        queryset=CierreCaja.objects.all(), source='cierre_caja', write_only=True, allow_null=True
    )

    class Meta:
        model = Pago
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class VentaDirectaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True, allow_null=True
    )
    usuario = serializers.StringRelatedField()
    metodo_pago = MetodoPagoSerializer(read_only=True)
    metodo_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=MetodoPago.objects.all(), source='metodo_pago', write_only=True
    )
    cierre_caja = CierreCajaSerializer(read_only=True)
    cierre_caja_id = serializers.PrimaryKeyRelatedField(
        queryset=CierreCaja.objects.all(), source='cierre_caja', write_only=True, allow_null=True
    )

    class Meta:
        model = VentaDirecta
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'subtotal', 'total')


class DetalleVentaSerializer(serializers.ModelSerializer):
    venta = VentaDirectaSerializer(read_only=True)
    venta_id = serializers.PrimaryKeyRelatedField(
        queryset=VentaDirecta.objects.all(), source='venta', write_only=True
    )
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = DetalleVenta
        fields = '__all__'
        read_only_fields = ('created_at', 'subtotal')


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


class CompraSerializer(serializers.ModelSerializer):
    proveedor = ProveedorSerializer(read_only=True)
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(), source='proveedor', write_only=True
    )
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Compra
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'total')


class DetalleCompraSerializer(serializers.ModelSerializer):
    compra = CompraSerializer(read_only=True)
    compra_id = serializers.PrimaryKeyRelatedField(
        queryset=Compra.objects.all(), source='compra', write_only=True
    )
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = DetalleCompra
        fields = '__all__'
        read_only_fields = ('created_at', 'subtotal')


class NotificacionSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Notificacion
        fields = '__all__'
        read_only_fields = ('created_at', 'fecha_lectura')


class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EstadisticasDiariasSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticasDiarias
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')