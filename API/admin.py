from django.contrib import admin
from .models import (
    Cliente, Categoria, Producto, MovimientoStock, TipoMesa, Mesa,
    MetodoPago, CierreCaja, Alquiler, Consumo, TransferenciaAlquiler,
    Pago, VentaDirecta, DetalleVenta, Proveedor, Compra, DetalleCompra,
    Notificacion, Configuracion, EstadisticasDiarias
)


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('descripcion_referencia', 'tipo_frecuencia', 'activo')
    list_filter = ('tipo_frecuencia', 'activo')
    search_fields = ('descripcion_referencia', 'preferencias', 'notas')


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_venta', 'stock_actual', 'stock_minimo', 'needs_restock', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'codigo_barras', 'descripcion')
    list_editable = ('stock_actual', 'stock_minimo')

    def needs_restock(self, obj):
        return obj.needs_restock
    needs_restock.boolean = True
    needs_restock.short_description = 'Necesita reposición'


class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'motivo', 'usuario', 'created_at')
    list_filter = ('tipo', 'producto')
    search_fields = ('producto__nombre', 'motivo')
    readonly_fields = ('created_at',)


class TipoMesaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_por_hora', 'precio_por_fraccion', 'activo')
    search_fields = ('nombre',)


class MesaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'tipo', 'estado', 'activo')
    list_filter = ('tipo', 'estado', 'activo')
    search_fields = ('nombre', 'codigo')


class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_display', 'requiere_referencia', 'activo')
    list_filter = ('activo',)


class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_apertura', 'fecha_cierre', 'monto_inicial', 'monto_final', 'ventas_totales', 'diferencia', 'esta_cerrada')
    list_filter = ('fecha_apertura', 'fecha_cierre')
    readonly_fields = ('ventas_totales', 'diferencia', 'created_at', 'updated_at')

    def esta_cerrada(self, obj):
        return obj.esta_cerrada
    esta_cerrada.boolean = True
    esta_cerrada.short_description = 'Cerrada'


class ConsumoInline(admin.TabularInline):
    model = Consumo
    extra = 0
    readonly_fields = ('subtotal', 'created_at')


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class AlquilerAdmin(admin.ModelAdmin):
    list_display = ('mesa', 'cliente', 'tiempo_inicio', 'tiempo_finalizacion', 'estado', 'monto_total', 'esta_pagado')
    list_filter = ('estado', 'mesa', 'tipo_tiempo')
    search_fields = ('mesa__nombre', 'cliente__descripcion_referencia', 'notas')
    inlines = [ConsumoInline, PagoInline]
    readonly_fields = ('created_at', 'updated_at')

    def esta_pagado(self, obj):
        return obj.esta_pagado
    esta_pagado.boolean = True
    esta_pagado.short_description = 'Pagado'


class ConsumoAdmin(admin.ModelAdmin):
    list_display = ('alquiler', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('producto',)
    search_fields = ('alquiler__mesa__nombre', 'producto__nombre')
    readonly_fields = ('subtotal', 'created_at')


class TransferenciaAlquilerAdmin(admin.ModelAdmin):
    list_display = ('alquiler_origen', 'alquiler_destino', 'mesa_origen', 'mesa_destino', 'tiempo_transferencia')
    list_filter = ('mesa_origen', 'mesa_destino')
    search_fields = ('alquiler_origen__mesa__nombre', 'alquiler_destino__mesa__nombre')
    readonly_fields = ('created_at', 'updated_at')


class PagoAdmin(admin.ModelAdmin):
    list_display = ('alquiler', 'fecha_hora', 'monto', 'metodo_pago', 'estado')
    list_filter = ('metodo_pago', 'estado')
    search_fields = ('alquiler__mesa__nombre', 'referencia')
    readonly_fields = ('created_at', 'updated_at')


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('subtotal',)


class VentaDirectaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_hora', 'total', 'metodo_pago', 'estado')
    list_filter = ('metodo_pago', 'estado')
    search_fields = ('cliente__descripcion_referencia', 'notas')
    inlines = [DetalleVentaInline]
    readonly_fields = ('created_at', 'updated_at')


class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('producto',)
    search_fields = ('venta__id', 'producto__nombre')
    readonly_fields = ('subtotal',)


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    readonly_fields = ('subtotal',)


class CompraAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'fecha_hora', 'total', 'estado')
    list_filter = ('proveedor', 'estado')
    search_fields = ('proveedor__nombre', 'numero_factura')
    inlines = [DetalleCompraInline]
    readonly_fields = ('created_at', 'updated_at')


class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('compra', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('producto',)
    search_fields = ('compra__id', 'producto__nombre')
    readonly_fields = ('subtotal',)


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'contacto', 'telefono', 'email')


class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'titulo', 'estado', 'created_at')
    list_filter = ('tipo', 'estado', 'usuario')
    search_fields = ('titulo', 'mensaje')
    readonly_fields = ('created_at', 'fecha_lectura')


class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('clave', 'valor', 'modificable')
    list_filter = ('modificable',)
    search_fields = ('clave', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')


class EstadisticasDiariasAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'ventas_totales', 'numero_alquileres', 'numero_ventas')
    list_filter = ('fecha',)
    search_fields = ('fecha',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(MovimientoStock, MovimientoStockAdmin)
admin.site.register(TipoMesa, TipoMesaAdmin)
admin.site.register(Mesa, MesaAdmin)
admin.site.register(MetodoPago, MetodoPagoAdmin)
admin.site.register(CierreCaja, CierreCajaAdmin)
admin.site.register(Alquiler, AlquilerAdmin)
admin.site.register(Consumo, ConsumoAdmin)
admin.site.register(TransferenciaAlquiler, TransferenciaAlquilerAdmin)
admin.site.register(Pago, PagoAdmin)
admin.site.register(VentaDirecta, VentaDirectaAdmin)
admin.site.register(DetalleVenta, DetalleVentaAdmin)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Compra, CompraAdmin)
admin.site.register(DetalleCompra, DetalleCompraAdmin)
admin.site.register(Notificacion, NotificacionAdmin)
admin.site.register(Configuracion, ConfiguracionAdmin)
admin.site.register(EstadisticasDiarias, EstadisticasDiariasAdmin)