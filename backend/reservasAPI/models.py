# reservasAPI/models.py
from django.db import models
from userAPI.models import UserProfile
from mesasAPI.models import Mesa, TipoRenta
from .exceptions import ReservaInvalidDatesException, ReservaConflictException


class Reserva(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reservas')
    tipo_renta = models.ForeignKey(TipoRenta, on_delete=models.PROTECT, related_name='reservas')
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField(blank=True, null=True)

    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    precio_total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_hora_inicio']

    def __str__(self):
        return f"Reserva {self.id} - {self.mesa.nombre} - {self.usuario.user.username}"

    def clean(self):
        if self.fecha_hora_inicio and self.fecha_hora_fin and self.fecha_hora_fin <= self.fecha_hora_inicio:
            raise ReservaInvalidDatesException()

        if self.estado != 'cancelada' and self.fecha_hora_inicio and self.fecha_hora_fin:
            conflictos = Reserva.objects.filter(
                mesa=self.mesa,
                estado__in=['pendiente', 'confirmada'],
                fecha_hora_inicio__lt=self.fecha_hora_fin,
                fecha_hora_fin__gt=self.fecha_hora_inicio
            ).exclude(pk=self.pk)

            if conflictos.exists():
                raise ReservaConflictException()

    def confirmar(self):
        if self.estado == 'pendiente':
            self.estado = 'confirmada'
            self.save()

    def cancelar(self):
        if self.estado in ['pendiente', 'confirmada']:
            self.estado = 'cancelada'
            self.save()

    def completar(self):
        if self.estado == 'confirmada':
            self.estado = 'completada'
            self.save()