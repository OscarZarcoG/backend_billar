# mesasAPI/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MesaViewSet

app_name = 'mesas'

router = DefaultRouter()
router.register(r'mesas', MesaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]