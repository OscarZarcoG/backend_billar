# mesasAPI/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from .models import Reservation, Session


@receiver(post_save, sender=Reservation)
def update_table_status_on_reservation_change(sender, instance, created, **kwargs):
    mesa = instance.table

    if instance.status == 'CO':
        if mesa.status == 'LI':
            mesa.status = 'RE'
            mesa.save(update_fields=['status'])

    elif instance.status in ['CA', 'CM']:
        if mesa.status == 'RE':
            otras_reservas = Reservation.objects.filter(
                table=mesa,
                status='CO'
            ).exclude(id=instance.id).exists()

            if not otras_reservas:
                mesa.status = 'LI'
                mesa.save(update_fields=['status'])


@receiver(post_save, sender=Session)
def update_reservations_on_session_start(sender, instance, created, **kwargs):
    if created or instance.status == 'EC':
        now = timezone.now()
        time_threshold = now - timedelta(hours=2)

        reservas = Reservation.objects.filter(
            table=instance.mesa,
            status='CO',
            start_datetime__lte=now,
            end_datetime__gte=time_threshold
        )

        # Marcar como completadas
        for reserva in reservas:
            with transaction.atomic():
                reserva.status = 'CM'
                reserva.save(update_fields=['status'])