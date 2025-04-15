# reservasAPI/admin.py
from django.contrib import admin
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'usuario', 'tipo_renta', 'fecha_hora_inicio',
                    'fecha_hora_fin', 'estado', 'precio_total', 'created_at')
    list_filter = ('estado', 'mesa', 'tipo_renta', 'created_at')
    search_fields = ('mesa__nombre', 'usuario__user__username', 'notas')
    date_hierarchy = 'fecha_hora_inicio'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información principal', {
            'fields': ('mesa', 'usuario', 'tipo_renta', 'estado')
        }),
        ('Fechas y horarios', {
            'fields': ('fecha_hora_inicio', 'fecha_hora_fin')
        }),
        ('Información adicional', {
            'fields': ('precio_total', 'notas')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirmar_reservas', 'cancelar_reservas', 'completar_reservas']

    def confirmar_reservas(self, request, queryset):
        count = 0
        for reserva in queryset.filter(estado='pendiente'):
            reserva.confirmar()
            count += 1
        self.message_user(request, f"{count} reservas han sido confirmadas correctamente.")

    confirmar_reservas.short_description = "Confirmar reservas seleccionadas"

    def cancelar_reservas(self, request, queryset):
        count = 0
        for reserva in queryset.filter(estado__in=['pendiente', 'confirmada']):
            reserva.cancelar()
            count += 1
        self.message_user(request, f"{count} reservas han sido canceladas correctamente.")

    cancelar_reservas.short_description = "Cancelar reservas seleccionadas"

    def completar_reservas(self, request, queryset):
        count = 0
        for reserva in queryset.filter(estado='confirmada'):
            reserva.completar()
            count += 1
        self.message_user(request, f"{count} reservas han sido completadas correctamente.")

    completar_reservas.short_description = "Marcar reservas seleccionadas como completadas"