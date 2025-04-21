# mesasAPI/serializers.py
from rest_framework import serializers
from .models import Mesa


class MesaSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Mesa
        fields = ['id', 'name', 'status', 'status_display', 'active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class MesaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['name', 'status', 'active']

    def validate_name(self, value):
        if Mesa.objects.filter(name=value).exists():
            from .exceptions import MesaAlreadyExists
            raise MesaAlreadyExists()
        return value


class MesaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['name', 'status', 'active']

    def validate_name(self, value):
        if Mesa.objects.filter(name=value).exclude(id=self.instance.id).exists():
            from .exceptions import MesaAlreadyExists
            raise MesaAlreadyExists()
        return value


class MesaStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['status']