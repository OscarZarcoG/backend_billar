from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCustomViewSet, GoogleLogin, GitHubLogin

urlpatterns = [
    # D J - R E S T - A U T H
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # S O C I A L   L O G I N
    path('auth/social/google/', GoogleLogin.as_view(), name='google-login'),
    path('auth/social/github/', GitHubLogin.as_view(), name='github-login'),
    
]

router = DefaultRouter()
router.register(r'auth/users', UserCustomViewSet, basename='users')

urlpatterns += [
    path('', include(router.urls)),
]
