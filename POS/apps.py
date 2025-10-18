# POS/apps.py
from django.apps import AppConfig


class PosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'POS'
    verbose_name = 'Sistema de Punto de Venta'

    def ready(self):
        import POS.signals