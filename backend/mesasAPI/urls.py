# mesasAPI/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'mesas', views.MesaViewSet)
router.register(r'sessions', views.SessionViewSet)
router.register(r'transfers', views.SessionTransferViewSet)
router.register(r'reservations', views.ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]