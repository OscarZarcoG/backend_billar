from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return getattr(settings, 'LOGIN_REDIRECT_URL', 'http://localhost:3000/')
