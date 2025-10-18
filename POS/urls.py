# POS/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, MarcaEmpresaViewSet, ProveedoresViewSet, ProductoViewSet,
    MovimientoStockViewSet, CompraViewSet, VentaViewSet, AlertaStockViewSet,
    DashboardStatsView, ProductosMasVendidosView
)

app_name = 'pos'

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'marcas', MarcaEmpresaViewSet, basename='marcas')
router.register(r'proveedores', ProveedoresViewSet, basename='proveedores')
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'movimientos-stock', MovimientoStockViewSet, basename='movimientos-stock')
router.register(r'compras', CompraViewSet, basename='compras')
router.register(r'ventas', VentaViewSet, basename='ventas')
router.register(r'alertas-stock', AlertaStockViewSet, basename='alertas-stock')

urlpatterns = [
    path('', include(router.urls)),

    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('reportes/productos-mas-vendidos/', ProductosMasVendidosView.as_view(), name='productos-mas-vendidos'),
]