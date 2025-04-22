# tipoRentaAPI/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoRentaViewSet

app_name = 'tipoRentaAPI'

router = DefaultRouter()
router.register(r'tipos-renta', TipoRentaViewSet, basename='tipos-renta')

urlpatterns = [
    path('', include(router.urls)),
]