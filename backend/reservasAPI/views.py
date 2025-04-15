# reservasAPI/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime

from .models import Reserva
from .serializers import (
    ReservaListSerializer,
    ReservaDetailSerializer,
    ReservaCreateUpdateSerializer
)
from rest_framework.response import Response
from .exceptions import (
    MesaNotAvailable, InvalidReservaState,
    DateRequired, InvalidDateFormat, InvalidTimeRange
)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['mesa', 'usuario', 'estado', 'tipo_renta']
    search_fields = ['mesa__nombre', 'usuario__user__username', 'notas']
    ordering_fields = ['fecha_hora_inicio', 'fecha_hora_fin', 'created_at', 'precio_total']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ReservaCreateUpdateSerializer
        return ReservaDetailSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado != 'pendiente':
            raise MesaNotAvailable()

        reserva.confirmar()
        serializer = self.get_serializer(reserva)
        raise Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado not in ['pendiente', 'confirmada']:
            raise InvalidReservaState()

        reserva.cancelar()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado != 'confirmada':
            raise InvalidReservaState()

        reserva.completar()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def disponibilidad(self, request):
        mesa_id = request.query_params.get('mesa_id')
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        if not fecha_inicio_str or not fecha_fin_str:
            raise DateRequired()

        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_fin = datetime.fromisoformat(fecha_fin_str)
        except ValueError:
            return InvalidDateFormat()

        if fecha_fin <= fecha_inicio:
            return InvalidTimeRange()

        filtro = {
            'estado__in': ['pendiente', 'confirmada'],
            'fecha_hora_inicio__lt': fecha_fin,
            'fecha_hora_fin__gt': fecha_inicio
        }

        if mesa_id:
            filtro['mesa_id'] = mesa_id

        reservas_solapadas = Reserva.objects.filter(**filtro)

        if mesa_id:
            disponible = not reservas_solapadas.exists()
            return Response({
                "disponible": disponible,
                "reservas_solapadas": ReservaListSerializer(reservas_solapadas,
                                                            many=True).data if reservas_solapadas.exists() else []
            })

        mesas_ocupadas = set(reserva.mesa.id for reserva in reservas_solapadas)
        return Response({
            "mesas_ocupadas": list(mesas_ocupadas),
            "reservas": ReservaListSerializer(reservas_solapadas, many=True).data
        })

    @action(detail=False, methods=['get'])
    def mis_reservas(self, request):
        reservas = Reserva.objects.filter(usuario__user=request.user)
        serializer = ReservaListSerializer(reservas, many=True)
        return Response(serializer.data)