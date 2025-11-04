# AUTH/apps.py
from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AUTH'
    verbose_name = 'Autenticación'
    
    def ready(self):
        # Crear/actualizar SocialApp para proveedores si hay credenciales en entorno
        # Evita fallos durante migraciones iniciales con try/except.
        import os
        from django.conf import settings
        try:
            from allauth.socialaccount.models import SocialApp
            from django.contrib.sites.models import Site
            from django.db.utils import OperationalError, ProgrammingError
        except Exception:
            return

        try:
            site_id = getattr(settings, 'SITE_ID', 1)
            site = Site.objects.get(pk=site_id)
        except (OperationalError, ProgrammingError, Exception):
            # DB no lista aún; salir silenciosamente
            return

        providers = [
            {
                'provider': 'google',
                'name': 'Google',
                'client_id': os.getenv('SOCIAL_GOOGLE_CLIENT_ID'),
                'secret': os.getenv('SOCIAL_GOOGLE_CLIENT_SECRET'),
            },
            {
                'provider': 'github',
                'name': 'GitHub',
                'client_id': os.getenv('SOCIAL_GITHUB_CLIENT_ID'),
                'secret': os.getenv('SOCIAL_GITHUB_CLIENT_SECRET'),
            },
        ]

        for p in providers:
            cid, sec = p['client_id'], p['secret']
            if not cid or not sec:
                continue
            try:
                app, created = SocialApp.objects.get_or_create(
                    provider=p['provider'],
                    name=p['name'],
                    defaults={'client_id': cid, 'secret': sec},
                )
                updated = False
                if app.client_id != cid:
                    app.client_id = cid
                    updated = True
                if app.secret != sec:
                    app.secret = sec
                    updated = True
                if updated:
                    app.save()
                if site not in app.sites.all():
                    app.sites.add(site)
            except (OperationalError, ProgrammingError):
                # DB no lista aún; ignorar
                continue