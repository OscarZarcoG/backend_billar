from allauth.account.adapter import DefaultAccountAdapter
from rest_framework.authtoken.models import Token
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        token, _ = Token.objects.get_or_create(user=user)
        frontend_url = getattr(settings, 'LOGIN_REDIRECT_URL', 'http://localhost:3000/')
        separator = '&' if '?' in frontend_url else '?'
        return f"{frontend_url}{separator}token={token.key}"