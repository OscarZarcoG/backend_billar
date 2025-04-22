# backend/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-@9xw1s_6tr1277ht-1&ht#!$e!a)rj^ck!97bfi2!aenbu23ax'

DEBUG = True

#ALLOWED_HOSTS = *
ALLOWED_HOSTS = ['192.168.247.113', '192.168.1.74', '192.168.1.22']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'userAPI',
    'mesasAPI',
    'clienteAPI',
    'tipoRentaAPI',
]
"""
    'sesionesAPI',
    'inventarioAPI',
    'consumosAPI',
    'pagosAPI',
    'configAPI',
    'reportesAPI',
"""


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

ASGI_APPLICATION = 'backend.asgi.application'


DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'bd_billar',
            'USER': 'postgres',
            'PASSWORD': 'dani123',
            'HOST': 'localhost',
            'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = (
    'http://localhost:3000',
    'http://192.168.1.74:8000',
    'http://192.168.1.22:3000',
)
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}


#'DEFAULT_AUTHENTICATION_CLASSES': [
#        'rest_framework.authentication.SessionAuthentication',
#       'rest_framework.authentication.TokenAuthentication',
#    ],


AUTHENTICATION_BACKENDS = [
    'userAPI.authentication.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')