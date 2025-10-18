# CLIENTS/serializers.py
from rest_framework import serializers
from .models import Customer


class CustomerBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'is_active', 'is_deleted', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields = ['id', 'is_active', 'is_deleted', 'created_at', 'updated_at', 'deleted_at']


class CustomerListSerializer(CustomerBaseSerializer):
    frecuency_display = serializers.CharField(
        source='get_frecuency_display',
        read_only=True
    )

    class Meta(CustomerBaseSerializer.Meta):
        fields = CustomerBaseSerializer.Meta.fields + [
            'description', 'frecuency', 'frecuency_display'
        ]
        read_only_fields = CustomerBaseSerializer.Meta.read_only_fields + [
            'frecuency_display'
        ]


class CustomerDetailSerializer(CustomerBaseSerializer):
    frecuency_display = serializers.CharField(
        source='get_frecuency_display',
        read_only=True
    )

    class Meta(CustomerBaseSerializer.Meta):
        fields = CustomerBaseSerializer.Meta.fields + [
            'description', 'frecuency', 'frecuency_display',
            'preferences'
        ]
        read_only_fields = CustomerBaseSerializer.Meta.read_only_fields + [
            'frecuency_display'
        ]

    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")

        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Description must be at least 3 characters long."
            )

        return value.strip().title()

    def validate_preferences(self, value):
        if value and len(value) > 1000:
            raise serializers.ValidationError(
                "Preferences cannot exceed 1000 characters."
            )
        return value

    def validate(self, attrs):
        description = attrs.get('description', '')

        queryset = Customer.objects.filter(
            description__iexact=description
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                'description': 'A customer with this description already exists.'
            })

        return attrs


class CustomerCreateSerializer(CustomerDetailSerializer):

    class Meta(CustomerDetailSerializer.Meta):
        fields = [field for field in CustomerDetailSerializer.Meta.fields
                  if field not in ['id', 'created_at', 'updated_at']]


class CustomerUpdateSerializer(CustomerDetailSerializer):
    description = serializers.CharField(required=False)
    frecuency = serializers.ChoiceField(
        choices=[
            ('OCCASIONAL', 'Occasional'),
            ('REGULAR', 'Regular'),
            ('FREQUENT', 'Frequent'),
        ],
        required=False
    )
