# CLIENTS/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Customer
from .serializers import (
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer
)
from .filters import CustomerFilter


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = CustomerFilter
    search_fields = ['description', 'preferences']
    ordering_fields = ['description', 'frecuency', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ['list', 'retrieve']:
            queryset = queryset.select_related()

        return queryset

    def get_serializer_class(self):
        serializer_map = {
            'list': CustomerListSerializer,
            'create': CustomerCreateSerializer,
            'update': CustomerUpdateSerializer,
            'partial_update': CustomerUpdateSerializer,
            'retrieve': CustomerDetailSerializer,
        }
        return serializer_map.get(self.action, CustomerDetailSerializer)

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        cache.delete_many(['customer_list', f'customer_{kwargs.get("pk")}'])
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        customer.delete()  # This will use soft delete from BaseModel

        cache.delete_many(['customer_list', f'customer_{customer.pk}'])

        return Response(
            {'message': 'Customer deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        customer = self.get_object()
        customer.restore()  # Use restore method from BaseModel

        cache.delete_many(['customer_list', f'customer_{customer.pk}'])

        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        customer = self.get_object()
        customer.delete()  # Use soft delete from BaseModel

        cache.delete_many(['customer_list', f'customer_{customer.pk}'])

        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def frequent_customers(self, request):
        frequent_customers = self.get_queryset().filter(
            frecuency='FREQUENT'
        )

        page = self.paginate_queryset(frequent_customers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(frequent_customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        queryset = self.get_queryset()

        stats = {
            'total_customers': queryset.count(),
            'frequent_customers': queryset.filter(
                frecuency='FREQUENT'
            ).count(),
            'regular_customers': queryset.filter(
                frecuency='REGULAR'
            ).count(),
            'occasional_customers': queryset.filter(
                frecuency='OCCASIONAL'
            ).count(),
            'customers_with_preferences': queryset.exclude(
                preferences__isnull=True
            ).exclude(preferences__exact='').count(),
        }

        return Response(stats)