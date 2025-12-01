from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import UserCustom


# B A S I C   S E R I A L I Z E R S
class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)


class UserCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'password',
            'phone', 'image_profile', 'birthday', 'gender', 'role',
            'created_at', 'updated_at',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
        
    def validate_role(self, value):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if self.instance:
                if self.instance.id == user.id and user.role == 'root':
                     raise serializers.ValidationError("Root cannot change their own role.")
            
            if user.role != 'root':
                 raise serializers.ValidationError("Only root users can assign roles.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


# D J - R E S T - A U T H   C U S T O M I Z A T I O N
class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    birthday = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=UserCustom.GENDER_CHOICES, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=UserCustom.ROLE_CHOICES, default='client', required=False)
    
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone': self.validated_data.get('phone', ''),
            'birthday': self.validated_data.get('birthday', None),
            'gender': self.validated_data.get('gender', ''),
            'role': self.validated_data.get('role', 'client'),
        })
        return data
    
    def custom_signup(self, request, user):
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone = self.cleaned_data.get('phone')
        user.birthday = self.cleaned_data.get('birthday')
        user.gender = self.cleaned_data.get('gender')
        user.role = self.cleaned_data.get('role')
        user.save()