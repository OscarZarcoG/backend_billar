# tipoRentaAPI/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import TipoRenta
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TipoRenta)
def log_tipo_renta_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Se ha creado un nuevo tipo de renta: {instance.name}")
    else:
        logger.info(f"Se ha actualizado el tipo de renta: {instance.name}")


@receiver(pre_save, sender=TipoRenta)
def validate_tipo_renta(sender, instance, **kwargs):
    if instance.price_for_unit <= 0:
        logger.warning(f"Se ha intentado establecer un precio no válido para {instance.name}")