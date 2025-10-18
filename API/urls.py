from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'clientes', views.ClienteViewSet)
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'movimientos-stock', views.MovimientoStockViewSet)
router.register(r'tipos-mesa', views.TipoMesaViewSet)
router.register(r'mesas', views.MesaViewSet)
router.register(r'metodos-pago', views.MetodoPagoViewSet)
router.register(r'cierres-caja', views.CierreCajaViewSet)
router.register(r'alquileres', views.AlquilerViewSet)
router.register(r'consumos', views.ConsumoViewSet)
router.register(r'transferencias-alquiler', views.TransferenciaAlquilerViewSet)
router.register(r'pagos', views.PagoViewSet)
router.register(r'ventas-directas', views.VentaDirectaViewSet)
router.register(r'detalles-venta', views.DetalleVentaViewSet)
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'compras', views.CompraViewSet)
router.register(r'detalles-compra', views.DetalleCompraViewSet)
router.register(r'notificaciones', views.NotificacionViewSet)
router.register(r'configuraciones', views.ConfiguracionViewSet)
router.register(r'estadisticas-diarias', views.EstadisticasDiariasViewSet)

urlpatterns = [
    path('', include(router.urls)),
]