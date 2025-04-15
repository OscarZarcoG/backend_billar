# reservasAPI/serializers.py
from rest_framework import serializers
from .models import Reserva
from userAPI.serializers import UserProfileSerializer
from mesasAPI.serializers import MesaSerializer, TipoRentaSerializer
from .exceptions import TimeRangeConflict, ReservaAlreadyExists, ReservaInvalidDatesException


class ReservaListSerializer(serializers.ModelSerializer):
    mesa_nombre = serializers.CharField(source='mesa.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.user.username', read_only=True)
    tipo_renta_nombre = serializers.CharField(source='tipo_renta.nombre', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'mesa', 'mesa_nombre', 'usuario', 'usuario_nombre',
            'tipo_renta_nombre', 'fecha_hora_inicio', 'fecha_hora_fin',
            'estado', 'precio_total', 'created_at'
        ]


class ReservaDetailSerializer(serializers.ModelSerializer):
    mesa = MesaSerializer(read_only=True)
    usuario = UserProfileSerializer(read_only=True)
    tipo_renta = TipoRentaSerializer(read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'mesa', 'usuario', 'tipo_renta', 'fecha_hora_inicio',
            'fecha_hora_fin', 'estado', 'precio_total', 'notas',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReservaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = [
            'mesa', 'usuario', 'tipo_renta', 'fecha_hora_inicio',
            'fecha_hora_fin', 'estado', 'precio_total', 'notas'
        ]

    def validate(self, data):
        if 'fecha_hora_fin' in data and 'fecha_hora_inicio' in data:
            if data['fecha_hora_fin'] <= data['fecha_hora_inicio']:
                raise ReservaInvalidDatesException()

        if self.instance and self.instance.pk and data.get('estado') != 'cancelada':
            mesa = data.get('mesa', self.instance.mesa)
            fecha_inicio = data.get('fecha_hora_inicio', self.instance.fecha_hora_inicio)
            fecha_fin = data.get('fecha_hora_fin', self.instance.fecha_hora_fin)

            conflictos = Reserva.objects.filter(
                mesa=mesa,
                estado__in=['pendiente', 'confirmada'],
                fecha_hora_inicio__lt=fecha_fin,
                fecha_hora_fin__gt=fecha_inicio
            ).exclude(pk=self.instance.pk)

            if conflictos.exists():
                raise ReservaAlreadyExists()

        return data