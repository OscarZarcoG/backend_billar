from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
import logging

from .models import Customer

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Customer)
def customer_pre_save(sender, instance, **kwargs):
    if instance.description:
        instance.description = instance.description.strip().title()

    if instance.pk:
        try:
            old_instance = Customer.objects.get(pk=instance.pk)
            changes = []

            fields_to_track = ['description', 'frecuency', 'deleted_at']
            for field in fields_to_track:
                old_value = getattr(old_instance, field)
                new_value = getattr(instance, field)
                if old_value != new_value:
                    changes.append(f'{field}: {old_value} → {new_value}')

            if changes:
                logger.info(
                    f'Customer {instance.pk} changes: {", ".join(changes)}'
                )

        except Customer.DoesNotExist:
            pass


@receiver(post_save, sender=Customer)
def customer_post_save(sender, instance, created, **kwargs):
    cache_keys = [
        'customer_list',
        f'customer_{instance.pk}',
        'customer_statistics',
        'frequent_customers'
    ]
    cache.delete_many(cache_keys)

    action = 'created' if created else 'updated'
    logger.info(f'Customer {instance.pk} ({instance.description}) {action}')

    if created:
        logger.info(f'Welcome new customer: {instance.description}')


@receiver(post_delete, sender=Customer)
def customer_post_delete(sender, instance, **kwargs):
    cache_keys = [
        'customer_list',
        f'customer_{instance.pk}',
        'customer_statistics',
        'frequent_customers'
    ]
    cache.delete_many(cache_keys)

    logger.info(f'Customer {instance.pk} ({instance.description}) deleted')