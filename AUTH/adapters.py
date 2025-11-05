from allauth.account.adapter import DefaultAccountAdapter
from dj_rest_auth.models import TokenModel
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        token, _ = TokenModel.objects.get_or_create(user=user)
        frontend_url = getattr(
            settings,
            'LOGIN_REDIRECT_URL',
            'https://frontend-billar.onrender.com/'
        )
        separator = '&' if '?' in frontend_url else '?'
        return f"{frontend_url}{separator}token={token.key}"