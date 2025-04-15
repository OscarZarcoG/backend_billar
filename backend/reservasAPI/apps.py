# reservasAPI/apps.py
from django.apps import AppConfig


class ReservasApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservasAPI'
    verbose_name = 'Gestión de Reservas'