from django.urls import path, include
from .views import UserCustomViewSet, GoogleLogin, GitHubLogin

urlpatterns = [
    # D J - R E S T - A U T H
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # S O C I A L   L O G I N
    path('auth/social/google/', GoogleLogin.as_view(), name='google-login'),
    path('auth/social/github/', GitHubLogin.as_view(), name='github-login'),
    
    # U S E R   M A N A G E M E N T
    path('auth/users/', UserCustomViewSet.as_view({'get': 'list'}), name='users-list'),
    path('auth/users/<int:pk>/', UserCustomViewSet.as_view({
        'get': 'retrieve',
        'put': 'update', 
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='users-detail'),
    
    # C U S T O M   A C T I O N S
    path('auth/users/by-role/', UserCustomViewSet.as_view({'get': 'users_by_role'}), name='users-by-role'),
    path('auth/users/<int:pk>/change-role/', UserCustomViewSet.as_view({'patch': 'change_user_role'}), name='change-role'),
    path('auth/users/<int:pk>/hard-delete/', UserCustomViewSet.as_view({'delete': 'hard_delete_user'}), name='hard-delete'),
    path('auth/users/<int:pk>/restore/', UserCustomViewSet.as_view({'patch': 'restore_user'}), name='restore-user'),
    path('auth/users/change-password/', UserCustomViewSet.as_view({'post': 'change_password'}), name='change-password'),
]