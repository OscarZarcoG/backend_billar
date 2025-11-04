# backend/settings.py
import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# ⚙️ CONFIGURACIÓN BÁSICA
# ========================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# ========================
# 📦 APLICACIONES
# ========================
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Dependencias externas
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_spectacular',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',

    # Apps locales
    'AUTH',
]

# ========================
# 🧩 MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

# ========================
# 🧠 TEMPLATES
# ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# ========================
# 🗄️ BASE DE DATOS
# ========================
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME', default='bd_billar'),
            'USER': config('DATABASE_USER', default='postgres'),
            'PASSWORD': config('DATABASE_PASSWORD', default='dani123'),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='5432'),
        }
    }

# ========================
# 🔐 AUTENTICACIÓN
# ========================
AUTH_USER_MODEL = 'AUTH.UserCustom'

# Backends de autenticación: Django + Allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Sites framework (requerido por django-allauth)
SITE_ID = config('SITE_ID', default=1, cast=int)

# Configuración de cuentas (django-allauth)
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'

# Configuración de social accounts (se usan SocialApp en DB con credenciales)
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# 🌍 INTERNACIONALIZACIÓN
# ========================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ========================
# 🧾 ARCHIVOS ESTÁTICOS / MEDIA
# ========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================
# 🌐 CORS
# ========================
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
CORS_ALLOW_CREDENTIALS = True

# ========================
# ⚙️ REST FRAMEWORK
# ========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ========================
# 🧭 SPECTACULAR (Swagger)
# ========================
SPECTACULAR_SETTINGS = {
    'TITLE': 'PoolZapp API',
    'DESCRIPTION': '''
    ## Sistema de Gestión de Billar
    
    API RESTful con:
    - Autenticación por token
    - Roles y permisos
    - Soft delete y restauración
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'docExpansion': 'none',
        'filter': True,
        'defaultModelExpandDepth': 3,
        'defaultModelsExpandDepth': 1,
        'tryItOutEnabled': True,
        'displayRequestDuration': True,
        'syntaxHighlight.theme': 'monokai',
    },
    'TAGS': [
        {'name': 'Autenticación', 'description': 'Login, registro y logout'},
        {'name': 'Usuarios', 'description': 'Gestión de usuarios y perfiles'},
        {'name': 'Roles', 'description': 'Gestión de roles y permisos'},
        {'name': 'Social', 'description': 'Login social (Google, GitHub)'},
    ],
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Desarrollo'},
        {'url': 'https://backend-billar.onrender.com', 'description': 'Producción'},
    ],
}

# ========================
# 🪵 LOGGING
# ========================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
