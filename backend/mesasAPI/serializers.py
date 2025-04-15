# mesasAPI/serializers.py
from rest_framework import serializers
from .models import Mesa, TipoRenta
from django.core.validators import MinValueValidator
from .exceptions import (
    NameRequired, PriceLess
)

class TipoRentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRenta
        fields = ['id', 'nombre', 'descripcion']
        extra_kwargs = {
            'nombre': {'required': True},
        }

    @staticmethod
    def validate_nombre(value):
        if not value.strip():
            raise NameRequired()
        return value


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = [
            'id', 'nombre', 'tipo', 'precio_hora', 'precio_media_hora',
            'estado', 'descripcion', 'activa', 'fecha_creacion',
            'ultima_actualizacion'
        ]
        extra_kwargs = {
            'nombre': {'required': True},
            'precio_hora': {
                'validators': [MinValueValidator(0)]
            },
            'precio_media_hora': {
                'validators': [MinValueValidator(0)]
            },
        }

    def validate(self, data):
        if 'precio_hora' in data and 'precio_media_hora' in data:
            if data['precio_media_hora'] >= data['precio_hora']:
                raise PriceLess()
        return data

    @staticmethod
    def validate_nombre(value):
        if not value.strip():
            raise NameRequired()
        return value