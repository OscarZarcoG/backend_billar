# clienteAPI/serializers.py
from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ClienteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ('reference_description', 'frequency_type', 'preferences', 'notes', 'active')


class ClienteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ('reference_description', 'frequency_type', 'preferences', 'notes', 'active')


class ClienteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class ClienteListSerializer(serializers.ModelSerializer):
    frequency_type_display = serializers.CharField(source='get_frequency_type_display', read_only=True)

    class Meta:
        model = Cliente
        fields = ('id', 'reference_description', 'frequency_type', 'frequency_type_display', 'active')