# AUTH/models.py
from django.contrib.auth.models import AbstractUser, UserManager
from core.models import BaseModel, BaseManager
from django.db import models


class UserCustomManager(BaseManager, UserManager):
    def get_queryset(self):
        return super(UserManager, self).get_queryset().filter(deleted_at__isnull=True)
    
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'client')
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'root')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class UserCustom(AbstractUser, BaseModel):
    objects = UserCustomManager()
    
    # Override groups and user_permissions with custom related_name to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre de usuario",
        help_text="Nombre de usuario",
        null=False
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="Nombres",
        help_text="Nombres",
        null = False
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name="Apellidos",
        help_text="Apellidos",
        null = False
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="Email",
        help_text="Email",
        null=False
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Password",
        help_text="Password",
        null=False
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        help_text="Teléfono",
        null = False,
        unique=True
    )
    image_profile = models.ImageField(
        upload_to='profile_pictures/',
        verbose_name="Imagen de perfil",
        help_text="Imagen de perfil",
        null=True,
        blank=True
    )
    birthday = models.DateField(
        verbose_name="Fecha de nacimiento",
        help_text="Fecha de nacimiento",
        null=True,
        blank=True,
    )
    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name="Genero",
        help_text="Genero",
        null=True,
        blank=True,
    )
    
    ROLE_CHOICES = [
        ('root', 'Root'),
        ('admin', 'Administrador'),
        ('client', 'Cliente'),
    ]
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Rol",
        db_index=True,
        help_text="Rol del usuario"
    )
    
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para establecer automáticamente
        is_staff e is_superuser según el rol del usuario
        """
        # Solo establecer permisos automáticamente si no se han establecido explícitamente
        if not hasattr(self, '_skip_role_permissions'):
            # Establecer permisos según el rol
            if self.role == 'root':
                self.is_staff = True
                self.is_superuser = True
            elif self.role == 'admin':
                self.is_staff = True
                self.is_superuser = False
            else:  # role == 'client'
                self.is_staff = False
                self.is_superuser = False
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-created_at']