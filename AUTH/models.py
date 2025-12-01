# AUTH/models.py
from django.contrib.auth.models import AbstractUser, UserManager
from core.models import BaseModel, BaseManager
from django.db import models
from django.utils import timezone


class UserCustomManager(BaseManager, UserManager):
    def get_queryset(self):
        return super().get_queryset()
    
    def _create_user(self, username, email, password, **extra_fields):
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

    email = models.EmailField(
        'email address',
        unique=True, 
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Phone",
        null=True,
        blank=True,
        unique=True
    )
    image_profile = models.ImageField(
        upload_to='profile_pictures/',
        verbose_name="Profile Picture",
        null=True,
        blank=True
    )
    birthday = models.DateField(
        verbose_name="Birthday",
        null=True,
        blank=True,
    )
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name="Gender",
        null=True,
        blank=True,
    )
    
    ROLE_CHOICES = [
        ('root', 'Root'),
        ('admin', 'Administrator'),
        ('client', 'Client'),
    ]
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Role",
        db_index=True,
    )
    
    def delete(self, hard_delete=False, **kwargs):
        super().delete(hard_delete=hard_delete, **kwargs)
        
        if not hard_delete:
            self.is_active = False
            self.save(update_fields=['is_active'])

    def restore(self):
        super().restore()
        self.is_active = True
        self.save(update_fields=['is_active'])
    
    def save(self, *args, **kwargs):
        if not hasattr(self, '_skip_role_permissions'):
            if self.role == 'root':
                self.is_staff = True
                self.is_superuser = True
            elif self.role == 'admin':
                self.is_staff = True
                self.is_superuser = False
            else:
                self.is_staff = False
                self.is_superuser = False
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
