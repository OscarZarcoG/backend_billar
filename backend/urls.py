# backend_billar/backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('AUTH.urls')),
    path('', lambda request: HttpResponse("Backend del sistema Billar funcionando ✅")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)