from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import check_password
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import UserCustom
from .serializers import UserCustomSerializer, LoginSerializer, UserRegistrationSerializer, UserRegistrationResponseSerializer, UserBasicSerializer
from .exceptions import (
    PasswordMismatch, PasswordRequired, UsernameRequired,
    EmailAlreadyExists, UserAlreadyExists,
    PermissionDenied, PasswordTooShort, EmailRequired
)
from core.exceptions import ValidationError, NotFoundError


@extend_schema_view(
    list=extend_schema(
        summary="Listar usuarios",
        description="Obtiene la lista de todos los usuarios activos del sistema",
        tags=["Usuarios"]
    ),
    retrieve=extend_schema(
        summary="Obtener usuario por ID",
        description="Obtiene los detalles de un usuario específico",
        tags=["Usuarios"]
    ),
    update=extend_schema(
        summary="Actualizar usuario",
        description="Actualiza completamente la información de un usuario",
        tags=["Usuarios"]
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente usuario",
        description="Actualiza parcialmente la información de un usuario",
        tags=["Usuarios"]
    ),
    destroy=extend_schema(
        summary="Desactivar usuario",
        description="Realiza un soft delete del usuario (desactivación)",
        tags=["Usuarios"]
    ),
)
class UserCustomViewSet(viewsets.ModelViewSet):
    queryset = UserCustom.objects.all()
    serializer_class = UserCustomSerializer
    
    def get_serializer_class(self):
        """Retorna el serializador apropiado según la acción"""
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return LoginSerializer
        return self.serializer_class
    
    def get_permissions(self):
        if self.action in ['create', 'register', 'login']:
            permission_classes = [AllowAny]
        elif self.action in ['me', 'update_profile', 'logout', 'change_password', 'users_by_role', 'hard_delete_user']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if 'role' in request.data:
            if request.user.role != 'root':
                raise PermissionDenied(detail='Solo el usuario root puede cambiar roles')
            if instance == request.user and request.user.role == 'root':
                raise PermissionDenied(detail='El usuario root no puede cambiar su propio rol')
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if 'role' in request.data:
            if request.user.role != 'root':
                raise PermissionDenied(detail='Solo el usuario root puede cambiar roles')
            if instance == request.user and request.user.role == 'root':
                raise PermissionDenied(detail='El usuario root no puede cambiar su propio rol')
        
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Registrar nuevo usuario",
        tags=["Autenticación"],
        request=UserRegistrationSerializer,
        responses={
            201: UserRegistrationResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Ejemplo de registro',
                value={
                        "username": "pedro_cliente",
                        "first_name": "Pedro",
                        "last_name": "Samano",
                        "email": "pedro.samano@example.com",
                        "password": "pedro123",
                        "password_confirm": "pedro123",
                        "phone": "987654321",
                        "birthday": "2004-11-03",
                        "gender": "male",
                        "role": "cliente"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Respuesta exitosa',
                value={
                    "user": {
                        "id": 1,
                        "username": "pedro_cliente",
                        "first_name": "Pedro",
                        "last_name": "Samano",
                        "email": "pedro.samano@example.com",
                        "phone": "987654321",
                        "birthday": "2004-11-03",
                        "gender": "male",
                        "role": "cliente"
                    },
                    "token": "a1b2c3d4e5f6g7h8i9j0",
                    "message": "Usuario registrado exitosamente"
                },
            ),
            OpenApiExample(
                'Errores de validación',
                value={
                    'errors': {
                        'username': [
                            'Este campo es requerido.'
                        ],
                        'email': [
                            'Este campo es requerido.'
                        ],
                        'password': [
                            'Este campo es requerido.'
                        ],
                        'password_confirm': [
                            'Este campo es requerido.'
                        ]
                    }
                },
                response_only=True,
            )
        ]
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        
        # El nombre de usuario es requerido
        if not username or username.strip() == '':
            raise UsernameRequired()
        
        # El email es requerido
        if not email or email.strip() == '':
            raise EmailRequired()
        
        # Contraseña es requerida
        if not password or password.strip() == '':
            raise PasswordRequired()
        
        # El usuario ya está registrado
        if username and UserCustom.objects.filter(username=username).exists():
            raise UserAlreadyExists()
        
        # El email ya está registrado
        if email and UserCustom.objects.filter(email=email).exists():
            raise EmailAlreadyExists()
        
        # Tamaño de contraseña 
        if password and len(password.strip()) < 8:
            raise PasswordTooShort()
        
        # Confirmación de contraseñas iguales
        if password and password_confirm and password != password_confirm:
            raise PasswordMismatch()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserRegistrationResponseSerializer(user).data,
                'token': token.key,
                'message': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'detail': 'Los datos proporcionados no son válidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Iniciar sesión",
        description="Autentica un usuario y retorna un token de acceso",
        tags=["Autenticación"],
        request=LoginSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Ejemplo de login',
                value={
                    'username': 'mi_usuario',
                    'password': 'mi_password'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Respuesta exitosa',
                value={
                    'user': {
                        'id': 1,
                        'username': 'mi_usuario',
                        'email': 'usuario@example.com',
                        'role': 'client'
                    },
                    'token': 'a1b2c3d4e5f6g7h8i9j0',
                    'message': 'Login exitoso'
                },
                response_only=True,
            ),
        ]
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserBasicSerializer(user).data,
                'token': token.key,
                'message': 'Login exitoso'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'detail': 'Los datos proporcionados no son válidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Cerrar sesión",
        description="Invalida el token de autenticación del usuario actual",
        tags=["Autenticación"],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Respuesta exitosa',
                value={
                    'message': 'Logout exitoso'
                },
                response_only=True,
            ),
        ]
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(
                detail='Error al cerrar sesión',
                meta={'error_details': str(e)}
            )
    
    @extend_schema(
        summary="Obtener perfil actual",
        description="Obtiene la información del usuario autenticado",
        tags=["Usuarios"],
        responses={
            200: UserCustomSerializer,
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Actualizar perfil",
        description="Actualiza la información del usuario autenticado",
        tags=["Usuarios"],
        request=UserCustomSerializer,
        responses={
            200: UserCustomSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        if 'role' in request.data and request.user.role != 'root':
            raise PermissionDenied(detail='Solo el usuario root puede cambiar roles')
        
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Perfil actualizado exitosamente'
            })
        
        raise ValidationError(
            detail='Los datos proporcionados no son válidos',
            field_errors=serializer.errors
        )
    
    @extend_schema(
        summary="Cambiar contraseña",
        description="Cambia la contraseña del usuario autenticado",
        tags=["Usuarios"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'old_password': {'type': 'string'},
                    'new_password': {'type': 'string'},
                },
                'required': ['old_password', 'new_password']
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Ejemplo de cambio de contraseña',
                value={
                    'old_password': 'password_actual',
                    'new_password': 'nueva_password123'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Respuesta exitosa',
                value={
                    'message': 'Contraseña cambiada exitosamente',
                    'token': 'nuevo_token_a1b2c3d4'
                },
                response_only=True,
            ),
        ]
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password:
            raise PasswordRequired(detail='La contraseña actual es requerida')
        if not new_password:
            raise PasswordRequired(detail='La nueva contraseña es requerida')
        
        if not check_password(old_password, request.user.password):
            raise PasswordMismatch(detail='La contraseña actual es incorrecta')
        
        request.user.set_password(new_password)
        request.user.save()
        
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        token = Token.objects.create(user=request.user)
        
        return Response({
            'message': 'Contraseña cambiada exitosamente',
            'token': token.key
        })
    
    @extend_schema(
        summary="Listar usuarios por rol",
        description="Obtiene usuarios filtrados por rol. Solo para admin y root.",
        tags=["Roles"],
        parameters=[
            OpenApiParameter(
                name='role',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Rol para filtrar (client, admin, root)',
                enum=['client', 'admin', 'root'],
                required=False
            ),
        ],
        responses={
            200: UserCustomSerializer(many=True),
            403: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def users_by_role(self, request):
        if request.user.role not in ['admin', 'root']:
            raise PermissionDenied()
        
        role = request.query_params.get('role')
        if role:
            users = UserCustom.objects.filter(role=role, is_active=True)
        else:
            users = UserCustom.objects.filter(is_active=True)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Cambiar rol de usuario",
        description="Cambia el rol de un usuario. Solo para usuario root.",
        tags=["Roles"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'role': {
                        'type': 'string',
                        'enum': ['client', 'admin', 'root']
                    }
                },
                'required': ['role']
            }
        },
        responses={
            200: UserCustomSerializer,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Cambiar a admin',
                value={'role': 'admin'},
                request_only=True,
            ),
        ]
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def change_user_role(self, request, pk=None):
        if request.user.role != 'root':
            raise PermissionDenied(detail='Solo el usuario root puede cambiar roles de otros usuarios')
        
        user = self.get_object()
        new_role = request.data.get('role')
        
        if not new_role or new_role not in ['client', 'admin', 'root']:
            raise ValidationError(detail='Rol inválido. Debe ser: client, admin o root')
        
        user.role = new_role
        user.save()
        
        return Response({
            'user': UserCustomSerializer(user).data,
            'message': f'Rol cambiado exitosamente a {new_role}'
        })
    
    @extend_schema(
        summary="Eliminar usuario completamente",
        description="Elimina permanentemente un usuario del sistema. Solo para root y admin.",
        tags=["Usuarios"],
        responses={
            204: None,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def hard_delete_user(self, request, pk=None):
        if request.user.role != 'root' and request.user.role != 'admin':
            raise PermissionDenied(detail='Solo los usuarios root o admin pueden realizar borrado completo')
        
        user = self.get_object()
        
        if user == request.user:
            raise PermissionDenied(detail='No puedes eliminarte a ti mismo')
        
        try:
            user.hard_delete(user=request.user)
            return Response({
                'message': 'Usuario eliminado completamente'
            }, status=status.HTTP_204_NO_CONTENT)
        except PermissionError as e:
            raise PermissionDenied(detail=str(e))
    
    @extend_schema(
        summary="Restaurar usuario",
        description="Restaura un usuario previamente desactivado. Solo para admin y root.",
        tags=["Usuarios"],
        responses={
            200: UserCustomSerializer,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def restore_user(self, request, pk=None):
        if request.user.role not in ['admin', 'root']:
            raise PermissionDenied(detail='Solo administradores y root pueden restaurar usuarios')
        
        try:
            user = UserCustom.objects.all_objects().get(pk=pk)
        except UserCustom.DoesNotExist:
            raise NotFoundError(detail='Usuario no encontrado')
        
        if not user.is_deleted:
            raise ValidationError(detail='El usuario no está borrado')
        
        user.restore()
        
        return Response({
            'user': UserCustomSerializer(user).data,
            'message': 'Usuario restaurado exitosamente'
        })