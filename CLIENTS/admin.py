# CLIENTS/admin.py
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'description', 'frecuency', 'frecuency_badge', 
        'has_preferences', 'created_at'
    ]

    list_filter = [
        'frecuency', 'created_at', 'updated_at', 'deleted_at'
    ]

    search_fields = ['description', 'preferences']

    list_editable = ['frecuency']

    readonly_fields = [
        'created_at', 'updated_at', 'deleted_at', 'is_deleted'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('description', 'frecuency')
        }),
        ('Additional Details', {
            'fields': ('preferences',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_deleted',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_customers', 'deactivate_customers', 'make_frequent']

    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    def frecuency_badge(self, obj):
        colors = {
            'OCCASIONAL': '#6c757d',
            'REGULAR': '#007bff',
            'FREQUENT': '#28a745',
        }
        color = colors.get(obj.frecuency, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color,
            obj.get_frecuency_display()
        )

    frecuency_badge.short_description = 'Frequency'

    def has_preferences(self, obj):
        return bool(obj.preferences)

    has_preferences.boolean = True
    has_preferences.short_description = 'Has Preferences'

    def activate_customers(self, request, queryset):
        count = 0
        for customer in queryset:
            if customer.is_deleted:
                customer.restore()
                count += 1
        
        self.message_user(
            request,
            f'{count} customer(s) were successfully activated.',
            messages.SUCCESS
        )

    activate_customers.short_description = "Activate selected customers"

    def deactivate_customers(self, request, queryset):
        count = 0
        for customer in queryset:
            if not customer.is_deleted:
                customer.delete()
                count += 1
        
        self.message_user(
            request,
            f'{count} customer(s) were successfully deactivated.',
            messages.SUCCESS
        )

    deactivate_customers.short_description = "Deactivate selected customers"

    def make_frequent(self, request, queryset):
        count = queryset.update(frecuency='FREQUENT')
        self.message_user(
            request,
            f'{count} customer(s) were marked as frequent.',
            messages.SUCCESS
        )

    make_frequent.short_description = "Mark selected customers as frequent"
