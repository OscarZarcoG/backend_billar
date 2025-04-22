# mesasAPI/serializers.py
from rest_framework import serializers
from .models import Mesa, Session, SessionTransfer, Reservation
from clienteAPI.serializers import ClienteSerializer
from tipoRentaAPI.serializers import TipoRentaSerializer
from django.contrib.auth.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class MesaSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Mesa
        fields = ['id', 'name', 'status', 'status_display', 'active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SessionSerializer(serializers.ModelSerializer):
    mesa_details = MesaSerializer(source='mesa', read_only=True)
    client_details = ClienteSerializer(source='client', read_only=True)
    user_details = UserSimpleSerializer(source='user', read_only=True)
    type_rent_details = TipoRentaSerializer(source='type_rent', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'mesa', 'mesa_details', 'client', 'client_details', 'user', 'user_details',
                  'type_rent', 'type_rent_details', 'start_time', 'end_time', 'total_time',
                  'time_import', 'consumo_import', 'total_import', 'status', 'status_display',
                  'created_at', 'updated_at']
        read_only_fields = ['total_import', 'created_at', 'updated_at', 'total_time']


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'mesa', 'client', 'type_rent', 'start_time']


class SessionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['end_time', 'time_import', 'consumo_import', 'status']


class SessionTransferSerializer(serializers.ModelSerializer):
    source_session_details = SessionSerializer(source='source_session', read_only=True)
    target_session_details = SessionSerializer(source='target_session', read_only=True)
    source_table_details = MesaSerializer(source='source_table', read_only=True)
    target_table_details = MesaSerializer(source='target_table', read_only=True)
    user_details = UserSimpleSerializer(source='user', read_only=True)

    class Meta:
        model = SessionTransfer
        fields = ['id', 'source_session', 'source_session_details', 'target_session',
                  'target_session_details', 'source_table', 'source_table_details',
                  'target_table', 'target_table_details', 'datetime', 'reason',
                  'user', 'user_details', 'created_at']
        read_only_fields = ['created_at']


class SessionTransferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionTransfer
        fields = ['source_session', 'target_table', 'reason']


class ReservationSerializer(serializers.ModelSerializer):
    table_details = MesaSerializer(source='table', read_only=True)
    client_details = ClienteSerializer(source='client', read_only=True)
    rent_type_details = TipoRentaSerializer(source='rent_type', read_only=True)
    user_details = UserSimpleSerializer(source='user', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'table', 'table_details', 'client', 'client_details',
                  'rent_type', 'rent_type_details', 'start_datetime', 'end_datetime',
                  'status', 'status_display', 'notes', 'user', 'user_details',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if 'start_datetime' in data and 'end_datetime' in data:
            if data['start_datetime'] >= data['end_datetime']:
                raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")

            # Check for overlapping reservations
            table = data.get('table', self.instance.table if self.instance else None)
            start = data.get('start_datetime')
            end = data.get('end_datetime')

            overlapping = Reservation.objects.filter(
                table=table,
                status__in=['PE', 'CO'],
                start_datetime__lt=end,
                end_datetime__gt=start
            )

            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError("Ya existe una reserva para este horario")

        return data