from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import UserCustom
from .serializers import UserCustomSerializer
from .permissions import IsRoot, IsAdminOrRoot


# S O C I A L   A U T H E N T I C A T I O N
@extend_schema(
    summary="Google social login",
    tags=["Social Authentication"],
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
)
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


@extend_schema(
    summary="GitHub social login",
    tags=["Social Authentication"],
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
)
class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client


# U S E R   M A N A G E M E N T
@extend_schema_view(
    list=extend_schema(summary="List users", tags=["Users"]),
    retrieve=extend_schema(summary="Get user", tags=["Users"]),
    update=extend_schema(summary="Update user", tags=["Users"]),
    partial_update=extend_schema(summary="Partial update", tags=["Users"]),
    destroy=extend_schema(summary="Deactivate user", tags=["Users"]),
)
class UserCustomViewSet(viewsets.ModelViewSet):
    queryset = UserCustom.objects.all()
    serializer_class = UserCustomSerializer
    permission_classes = [IsAuthenticated]
    
    
    
    @extend_schema(
        summary="Filter users by role",
        tags=["Roles"],
        parameters=[
            OpenApiParameter(
                name='role',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=['client', 'admin', 'root'],
                required=False
            ),
        ],
        responses={200: UserCustomSerializer(many=True), 403: OpenApiTypes.OBJECT},
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrRoot], url_path='by-role')
    def users_by_role(self, request):
        role = request.query_params.get('role')
        users = UserCustom.objects.filter(role=role, is_active=True) if role else UserCustom.objects.filter(is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Change user role",
        tags=["Roles"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'role': {'type': 'string', 'enum': ['client', 'admin', 'root']}
                },
                'required': ['role']
            }
        },
        responses={200: UserCustomSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsRoot], url_path='change-role')
    def change_user_role(self, request, pk=None):
        user = self.get_object()
        new_role = request.data.get('role')
        
        if not new_role or new_role not in ['client', 'admin', 'root']:
            raise ValidationError(detail='Invalid role')
            
        if user == request.user:
             raise PermissionDenied(detail='Root cannot change own role')
        
        user.role = new_role
        user.save()
        
        return Response({
            'user': UserCustomSerializer(user).data,
            'message': f'Role changed to {new_role}'
        })
    
    @extend_schema(
        summary="Hard delete user",
        tags=["Users"],
        responses={204: None, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=['delete'], permission_classes=[IsAdminOrRoot], url_path='hard-delete')
    def hard_delete_user(self, request, pk=None):
        user = self.get_object()
        
        if user == request.user:
            raise PermissionDenied(detail='Cannot delete yourself')
        
        try:
            user.hard_delete()
            return Response({'message': 'User deleted permanently'}, status=status.HTTP_204_NO_CONTENT)
        except PermissionError as e:
            raise PermissionDenied(detail=str(e))
    
    @extend_schema(
        summary="Restore user",
        tags=["Users"],
        responses={200: UserCustomSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOrRoot], url_path='restore')
    def restore_user(self, request, pk=None):
        user = self.get_object()
        user.restore()
        return Response({
            'user': UserCustomSerializer(user).data,
            'message': 'User restored successfully'
        })
