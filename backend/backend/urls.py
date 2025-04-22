# backend_billar/backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('userAPI.urls')),
    path('api/mesas/', include('mesasAPI.urls')),
    path('api/clientes/', include('clienteAPI.urls')),
    path('api/tipos-renta/', include('tipoRentaAPI.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)