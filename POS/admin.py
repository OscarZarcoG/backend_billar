# POS/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Categoria, Marca_Empresa, Proveedores, Producto, MovimientoStock,
    Compra, DetalleCompra, Venta, DetalleVenta, AlertaStock
)

""" C A T E G O R I A S   A D M I N """
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'total_productos', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    list_per_page = 25

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def total_productos(self, obj):
        return obj.productos.filter(status=True).count()

    total_productos.short_description = 'Total Productos'

    actions = ['activar_categorias', 'desactivar_categorias']

    def activar_categorias(self, request, queryset):
        queryset.update(status=True, deleted_at=None)
        self.message_user(request, f'{queryset.count()} categorías activadas.')

    activar_categorias.short_description = 'Activar categorías seleccionadas'

    def desactivar_categorias(self, request, queryset):
        for categoria in queryset:
            categoria.soft_delete()
        self.message_user(request, f'{queryset.count()} categorías desactivadas.')

    desactivar_categorias.short_description = 'Desactivar categorías seleccionadas'


""" M A R C A S   E M P R E S A S   A D M I N """
@admin.register(Marca_Empresa)
class MarcaEmpresaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'logo_preview', 'sitio_web', 'telefono', 'total_productos', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['nombre', 'sitio_web', 'telefono']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at', 'logo_preview']
    list_per_page = 25

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'logo', 'logo_preview')
        }),
        ('Contacto', {
            'fields': ('sitio_web', 'telefono')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.logo.url)
        return "Sin logo"

    logo_preview.short_description = 'Vista previa'

    def total_productos(self, obj):
        return obj.productos.filter(status=True).count()

    total_productos.short_description = 'Total Productos'


""" P R O V E E D O R E S   A D M I N """
@admin.register(Proveedores)
class ProveedoresAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'telefono', 'email', 'total_productos', 'status', 'created_at']
    list_filter = ['empresa', 'status', 'created_at']
    search_fields = ['nombre', 'telefono', 'email', 'empresa__nombre']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    list_per_page = 25
    autocomplete_fields = ['empresa']

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'empresa')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def total_productos(self, obj):
        return obj.productos_suministrados.filter(status=True).count()

    total_productos.short_description = 'Productos Suministrados'


""" P R O D U C T O S   A D M I N """
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'codigo_barras', 'marca', 'categoria', 'precio_venta',
        'stock_actual', 'estado_stock', 'status', 'created_at'
    ]
    list_filter = [
        'marca', 'categoria', 'proveedor_principal', 'es_servicio', 'status', 'created_at'
    ]
    search_fields = ['nombre', 'codigo_barras', 'sku', 'descripcion']
    readonly_fields = [
        'created_at', 'updated_at', 'deleted_at', 'sku', 'ganancia_absoluta_display',
        'ganancia_porcentual_display', 'precio_con_impuesto_display', 'imagen_preview'
    ]
    list_per_page = 25
    autocomplete_fields = ['marca', 'categoria', 'proveedor_principal']

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo_barras', 'sku', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('marca', 'categoria', 'proveedor_principal')
        }),
        ('Precios y Márgenes', {
            'fields': (
                'precio_compra', 'precio_venta', 'margen_ganancia',
                'ganancia_absoluta_display', 'ganancia_porcentual_display',
                'impuesto', 'precio_con_impuesto_display'
            )
        }),
        ('Stock', {
            'fields': ('stock_actual', 'stock_minimo', 'stock_maximo')
        }),
        ('Características', {
            'fields': ('peso', 'dimensiones', 'es_servicio')
        }),
        ('Imagen', {
            'fields': ('imagen', 'imagen_preview')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.imagen.url)
        return "Sin imagen"

    imagen_preview.short_description = 'Vista previa'

    def ganancia_absoluta_display(self, obj):
        return f"${obj.ganancia_absoluta:.2f}"

    ganancia_absoluta_display.short_description = 'Ganancia Absoluta'

    def ganancia_porcentual_display(self, obj):
        return f"{obj.ganancia_porcentual:.2f}%"

    ganancia_porcentual_display.short_description = 'Ganancia %'

    def precio_con_impuesto_display(self, obj):
        return f"${obj.precio_con_impuesto:.2f}"

    precio_con_impuesto_display.short_description = 'Precio con Impuesto'

    def estado_stock(self, obj):
        if obj.es_servicio:
            return format_html('<span style="color: blue;">Servicio</span>')
        elif obj.stock_actual == 0:
            return format_html('<span style="color: red;">Sin Stock</span>')
        elif obj.requiere_reposicion:
            return format_html('<span style="color: orange;">Stock Bajo</span>')
        elif obj.exceso_stock:
            return format_html('<span style="color: purple;">Exceso</span>')
        else:
            return format_html('<span style="color: green;">Normal</span>')

    estado_stock.short_description = 'Estado Stock'

    actions = ['actualizar_precios_por_margen']

    def actualizar_precios_por_margen(self, request, queryset):
        count = 0
        for producto in queryset:
            if producto.margen_ganancia > 0:
                producto.actualizar_precio_venta_por_margen()
                producto.save()
                count += 1
        self.message_user(request, f'{count} productos actualizados.')

    actualizar_precios_por_margen.short_description = 'Actualizar precios por margen'


""" M O V I M I E N T O S   S T O C K   A D M I N """
@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = [
        'producto', 'tipo_movimiento', 'cantidad', 'stock_anterior',
        'stock_nuevo', 'usuario', 'fecha', 'referencia'
    ]
    list_filter = ['tipo_movimiento', 'fecha', 'usuario']
    search_fields = ['producto__nombre', 'referencia', 'observaciones']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    date_hierarchy = 'fecha'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


""" D E T A L L E   C O M P R A   I N L I N E """


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    readonly_fields = ['subtotal_display']
    autocomplete_fields = ['producto']

    def subtotal_display(self, obj):
        if obj.id:
            return f"${obj.subtotal:.2f}"
        return "$0.00"

    subtotal_display.short_description = 'Subtotal'


""" C O M P R A S   A D M I N """
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'numero_factura', 'proveedor', 'estado', 'fecha_pedido',
        'fecha_recepcion', 'total_display', 'usuario'
    ]
    list_filter = ['estado', 'proveedor', 'fecha_pedido', 'usuario']
    search_fields = ['numero_factura', 'proveedor__nombre']
    readonly_fields = [
        'created_at', 'updated_at', 'deleted_at', 'subtotal_display',
        'total_display', 'cantidad_items_display'
    ]
    inlines = [DetalleCompraInline]
    list_per_page = 25
    date_hierarchy = 'fecha_pedido'
    autocomplete_fields = ['proveedor']

    fieldsets = (
        ('Información General', {
            'fields': ('numero_factura', 'proveedor', 'usuario')
        }),
        ('Fechas', {
            'fields': ('fecha_pedido', 'fecha_recepcion')
        }),
        ('Estado y Totales', {
            'fields': (
                'estado', 'subtotal_display', 'descuento', 'impuesto',
                'total_display', 'cantidad_items_display'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def subtotal_display(self, obj):
        return f"${obj.subtotal:.2f}"

    subtotal_display.short_description = 'Subtotal'

    def total_display(self, obj):
        return f"${obj.total:.2f}"

    total_display.short_description = 'Total'

    def cantidad_items_display(self, obj):
        return obj.cantidad_items

    cantidad_items_display.short_description = 'Items'

    actions = ['marcar_como_recibidas']

    def marcar_como_recibidas(self, request, queryset):
        count = 0
        for compra in queryset.filter(estado='PENDIENTE'):
            compra.marcar_como_recibida()
            count += 1
        self.message_user(request, f'{count} compras marcadas como recibidas.')

    marcar_como_recibidas.short_description = 'Marcar como recibidas'


""" D E T A L L E   V E N T A   I N L I N E """
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['subtotal_display', 'ganancia_display']
    autocomplete_fields = ['producto']

    def subtotal_display(self, obj):
        if obj.id:
            return f"${obj.subtotal:.2f}"
        return "$0.00"

    subtotal_display.short_description = 'Subtotal'

    def ganancia_display(self, obj):
        if obj.id:
            return f"${obj.ganancia:.2f}"
        return "$0.00"

    ganancia_display.short_description = 'Ganancia'


""" V E N T A S   A D M I N """
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = [
        'numero_ticket', 'cliente', 'metodo_pago', 'estado', 'fecha',
        'total_display', 'ganancia_display', 'usuario'
    ]
    list_filter = ['metodo_pago', 'estado', 'fecha', 'usuario']
    search_fields = ['numero_ticket', 'cliente__nombre']
    readonly_fields = [
        'created_at', 'updated_at', 'deleted_at', 'numero_ticket',
        'subtotal_display', 'total_display', 'ganancia_display', 'cantidad_items_display'
    ]
    inlines = [DetalleVentaInline]
    list_per_page = 25
    date_hierarchy = 'fecha'

    fieldsets = (
        ('Información General', {
            'fields': ('numero_ticket', 'usuario', 'cliente')
        }),
        ('Pago y Estado', {
            'fields': ('metodo_pago', 'estado')
        }),
        ('Totales', {
            'fields': (
                'subtotal_display', 'descuento', 'impuesto',
                'total_display', 'ganancia_display', 'cantidad_items_display'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def subtotal_display(self, obj):
        return f"${obj.subtotal:.2f}"

    subtotal_display.short_description = 'Subtotal'

    def total_display(self, obj):
        return f"${obj.total:.2f}"

    total_display.short_description = 'Total'

    def ganancia_display(self, obj):
        return f"${obj.ganancia:.2f}"

    ganancia_display.short_description = 'Ganancia'

    def cantidad_items_display(self, obj):
        return obj.cantidad_items

    cantidad_items_display.short_description = 'Items'


""" A L E R T A S   S T O C K   A D M I N """
@admin.register(AlertaStock)
class AlertaStockAdmin(admin.ModelAdmin):
    list_display = [
        'producto', 'tipo_alerta', 'leida', 'usuario_asignado', 'created_at'
    ]
    list_filter = ['tipo_alerta', 'leida', 'created_at']
    search_fields = ['producto__nombre', 'mensaje']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50

    actions = ['marcar_como_leidas', 'generar_alertas_stock']

    def marcar_como_leidas(self, request, queryset):
        queryset.update(leida=True)
        self.message_user(request, f'{queryset.count()} alertas marcadas como leídas.')

    marcar_como_leidas.short_description = 'Marcar como leídas'

    def generar_alertas_stock(self, request, queryset):
        AlertaStock.generar_alertas_stock()
        self.message_user(request, 'Alertas de stock generadas correctamente.')

    generar_alertas_stock.short_description = 'Generar alertas de stock'


admin.site.site_header = "Sistema POS - Panel de Administración"
admin.site.site_title = "POS Admin"
admin.site.index_title = "Bienvenido al Panel de Administración"