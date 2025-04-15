# mesasAPI/urls.py
from django.urls import path
from .views import (
    MesaListCreateView,
    MesaDetailView,
    TipoRentaListCreateView,
    TipoRentaDetailView
)

urlpatterns = [
    path('mesas/', MesaListCreateView.as_view(), name='mesa-list-create'),
    path('mesas/<int:pk>/', MesaDetailView.as_view(), name='mesa-detail'),
    path('tipo-rentas/', TipoRentaListCreateView.as_view(), name='tipo-renta-list-create'),
    path('tipo-rentas/<int:pk>/', TipoRentaDetailView.as_view(), name='tipo-renta-detail'),
]