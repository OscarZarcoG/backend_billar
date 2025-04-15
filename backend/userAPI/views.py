# userAPI/views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from .serializers import UserSerializer
from .exceptions import (
    UserDoesNotExist,  PermissionDenied, InvalidCredentials,
    UsernameRequired, PasswordRequired,
)
from .responses import  (
    UserUpdatedSuccess, UserDeletedSuccess, UserCreatedSuccess,
    UserLoginSuccess, UserLogoutSuccess
)
from django.contrib.auth import authenticate, login, logout
from core.exceptions import DatabaseError, BaseCustomException
from core.responses import BaseSuccessResponse


class UserLoginView(APIView):
    @staticmethod
    def post(request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise [UsernameRequired(), PasswordRequired()]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            return UserLoginSuccess(data=serializer.data).to_response()
        else:
            raise InvalidCredentials()


class UserLogoutView(APIView):
    @staticmethod
    def post(self, request):
        logout(request)
        return UserLogoutSuccess().to_response()


class UserCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @staticmethod
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return UserCreatedSuccess(data=UserSerializer(user).data).to_response()
            else:
                raise BaseCustomException(detail=serializer.errors)
        except Exception as e:
            if isinstance(e, BaseCustomException):
                raise e
            raise DatabaseError(str(e))


class UserDetailView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @staticmethod
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user != request.user:
                raise PermissionDenied()

            serializer = UserSerializer(user)
            return BaseSuccessResponse(data=serializer.data).to_response()
        except User.DoesNotExist:
            raise UserDoesNotExist()
        except Exception as e:
            raise DatabaseError(str(e))

    @staticmethod
    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user != request.user:
                raise PermissionDenied()

            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return UserUpdatedSuccess(data=serializer.data).to_response()
            else:
                raise BaseCustomException(detail=serializer.errors)
        except User.DoesNotExist:
            raise UserDoesNotExist()
        except Exception as e:
            raise DatabaseError(str(e))

    @staticmethod
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user != request.user:
                raise PermissionDenied()

            user.delete()
            return UserDeletedSuccess().to_response()
        except User.DoesNotExist:
            raise UserDoesNotExist()
        except Exception as e:
            raise DatabaseError(str(e))