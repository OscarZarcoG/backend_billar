# AUTH/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UserCustom
from .exceptions import (
    PasswordMismatch, PasswordRequired, UsernameRequired, EmailRequired,
    UserAlreadyExists, EmailAlreadyExists, PasswordTooShort, PhoneInvalid,
    InvalidCredentials, UserDoesNotExist, PermissionDenied
)

class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email'
        )

class UserCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'phone',
            'image_profile',
            'birthday',
            'gender',
            'role',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = (attrs.get('username') or '').strip()
        password = (attrs.get('password') or '').strip()
        
        if not username:
            raise UsernameRequired()
        if not password:
            raise PasswordRequired()
        
        user = authenticate(username=username, password=password)
        if not user:
            try:
                user_obj = UserCustom.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except UserCustom.DoesNotExist:
                raise UserDoesNotExist()
        
        if not user:
            raise InvalidCredentials()
        
        if not user.is_active:
            raise PermissionDenied(detail='La cuenta está desactivada.')
        
        attrs['user'] = user
        return attrs

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserCustom
        fields = (
            'username',
            'first_name', 
            'last_name',
            'email',
            'password',
            'password_confirm',
            'phone',
            'birthday',
            'gender',
            'role'
        )
        
    def validate(self, attrs):
        username = (attrs.get('username') or '').strip()
        email = (attrs.get('email') or '').strip()
        password = (attrs.get('password') or '').strip()
        password_confirm = (attrs.get('password_confirm') or '').strip()
        phone = attrs.get('phone')
        phone_str = (str(phone).strip() if phone is not None else None)

        # Requeridos
        if not username:
            raise UsernameRequired()
        if not email:
            raise EmailRequired()
        if not password:
            raise PasswordRequired()

        # Unicidad
        if UserCustom.objects.filter(username=username).exists():
            raise UserAlreadyExists()
        if UserCustom.objects.filter(email=email).exists():
            raise EmailAlreadyExists()

        # Seguridad contraseña
        if len(password) < 8:
            raise PasswordTooShort()

        # Confirmación de contraseña
        if password_confirm and password != password_confirm:
            raise PasswordMismatch()

        # Validación de teléfono
        if phone_str and len(phone_str) < 10:
            raise PhoneInvalid()

        # Normalización
        attrs['username'] = username
        attrs['email'] = email
        attrs['password'] = password
        attrs['password_confirm'] = password_confirm
        if phone is not None:
            attrs['phone'] = phone_str
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        
        password = validated_data.pop('password')
        user = UserCustom(**validated_data)
        user.set_password(password)
        user.save()
        return user