# CLIENTS/apps.py
from django.apps import AppConfig

class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CLIENTS'
    verbose_name = 'Client Management'

    def ready(self):
        try:
            import CLIENTS.signals
        except ImportError:
            pass