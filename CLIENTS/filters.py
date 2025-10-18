# CLIENTS/filters.py
import django_filters
from django.db import models
from .models import Customer


class CustomerFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        help_text='Filter by description (case-insensitive contains)'
    )

    frecuency = django_filters.ChoiceFilter(
        choices=[
            ('OCCASIONAL', 'Occasional'),
            ('REGULAR', 'Regular'),
            ('FREQUENT', 'Frequent'),
        ],
        help_text='Filter by purchase frequency'
    )

    is_frequent = django_filters.BooleanFilter(
        method='filter_is_frequent',
        help_text='Filter frequent customers (frequency=FREQUENT)'
    )

    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter customers created after this date'
    )

    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter customers created before this date'
    )

    has_preferences = django_filters.BooleanFilter(
        method='filter_has_preferences',
        help_text='Filter customers with/without preferences'
    )

    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Search in description and preferences'
    )

    class Meta:
        model = Customer
        fields = {
            'frecuency': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
            'deleted_at': ['exact', 'gte', 'lte'],
        }

    def filter_is_frequent(self, queryset, name, value):
        if value is True:
            return queryset.filter(frecuency='FREQUENT')
        elif value is False:
            return queryset.exclude(frecuency='FREQUENT')
        return queryset

    def filter_has_preferences(self, queryset, name, value):
        if value is True:
            return queryset.filter(
                models.Q(preferences__isnull=False) &
                ~models.Q(preferences__exact='')
            )
        elif value is False:
            return queryset.filter(
                models.Q(preferences__isnull=True) |
                models.Q(preferences__exact='')
            )
        return queryset

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            models.Q(description__icontains=value) |
            models.Q(preferences__icontains=value)
        ).distinct()
