# tipoRentaAPI/serializers.py
from rest_framework import serializers
from .models import TipoRenta


class TipoRentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRenta
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TipoRentaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRenta
        fields = ('name', 'price_for_unit', 'description', 'is_open_time', 'default_duration', 'active')

    def validate(self, data):
        if data.get('price_for_unit', 0) <= 0:
            raise serializers.ValidationError("El precio por unidad debe ser mayor que cero.")

        if data.get('default_duration', 0) <= 0:
            raise serializers.ValidationError("La duración predeterminada debe ser mayor que cero.")

        return data


class TipoRentaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRenta
        fields = ('name', 'price_for_unit', 'description', 'is_open_time', 'default_duration', 'active')

    def validate(self, data):
        if 'price_for_unit' in data and data['price_for_unit'] <= 0:
            raise serializers.ValidationError("El precio por unidad debe ser mayor que cero.")

        if 'default_duration' in data and data['default_duration'] <= 0:
            raise serializers.ValidationError("La duración predeterminada debe ser mayor que cero.")

        return data


class TipoRentaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRenta
        fields = ('id', 'name', 'price_for_unit', 'is_open_time', 'default_duration', 'active')