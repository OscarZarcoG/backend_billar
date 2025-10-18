# CLIENTS/models.py
from django.db import models
from core.models import BaseModel, BaseManager

class CustomerCustomManager(BaseManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


""" C L I E N T S """
FRECUENCY_CHOICES = (
    ('OCCASIONAL', 'Occasional'),
    ('REGULAR', 'Regular'),
    ('FREQUENT', 'Frequent'),
)

class Customer(BaseModel):
    frecuency = models.CharField(
        max_length=10,
        choices=FRECUENCY_CHOICES,
        default='OCCASIONAL',
        verbose_name="Purchase Frequency",
        help_text="How often this customer makes purchases."
    )
    description = models.CharField(
        max_length=100,
        verbose_name="Description",
        help_text="A descriptive reference for this customer."
    )
    preferences = models.TextField(
        blank=True,
        null=True,
        verbose_name="Preferences",
        help_text="Customer's specific preferences or notes."
    )

    def __str__(self):
        return self.description

    class Meta(BaseModel.Meta):
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['description']
        indexes = [
            models.Index(fields=['description']),
            models.Index(fields=['frecuency']),
            models.Index(fields=['deleted_at']),
        ]