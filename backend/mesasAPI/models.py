# mesasAPI/models.py
from django.db import models
from django.core.validators import MinValueValidator


class Mesa(models.Model):
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    precio_hora = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    precio_media_hora = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    ESTADO_CHOICES = (
        ('libre', 'Libre'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
        ('mantenimiento', 'En Mantenimiento'),
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='libre')
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"

    def esta_disponible(self):
        return self.estado == 'libre' and self.activa


class TipoRenta(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Tipo de renta'
        verbose_name_plural = 'Tipos de renta'

    def __str__(self):
        return self.nombre