import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# B A S I C   C O N F I G U R A T I O N
SECRET_KEY = config('SECRET_KEY', default='django-insecure-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# A P P L I C A T I O N S
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'AUTH',
    'core',
]

# M I D D L E W A R E
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

# T E M P L A T E S
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

# D A T A B A S E
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

# A U T H E N T I C A T I O N
AUTH_USER_MODEL = 'AUTH.UserCustom'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = config('SITE_ID', default=1, cast=int)

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none' if DEBUG else 'mandatory'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_ADAPTER = 'AUTH.adapters.CustomAccountAdapter'

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

# I N T E R N A T I O N A L I Z A T I O N
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# S T A T I C   F I L E S
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# C O R S
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
CORS_ALLOW_CREDENTIALS = True

# R E S T   F R A M E W O R K
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        #'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# D J - R E S T - A U T H
REST_AUTH = {
    'REGISTER_SERIALIZER': 'AUTH.serializers.CustomRegisterSerializer',
    'USER_DETAILS_SERIALIZER': 'AUTH.serializers.UserCustomSerializer',
    'TOKEN_MODEL': 'rest_framework.authtoken.models.Token',
    'SESSION_LOGIN': False,
    'USE_JWT': False,
}

# A P I   D O C U M E N T A T I O N
SPECTACULAR_SETTINGS = {
    'TITLE': 'PoolZapp API',
    'DESCRIPTION': 'RESTful API with token authentication, roles and permissions',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'POSTPROCESSING_HOOKS': ['backend.schema_hooks.organize_tags'],
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
        {'name': 'Authentication', 'description': 'Login, registration and logout'},
        {'name': 'Users', 'description': 'User management'},
        {'name': 'Roles', 'description': 'Role management'},
        {'name': 'Social Authentication', 'description': 'Social login (Google, GitHub)'},
    ],
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development'},
    ],
}

# L O G G I N G
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

# R E D I R E C T   U R L S
if DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
    LOGIN_REDIRECT_URL = 'http://localhost:3000/'
    LOGOUT_REDIRECT_URL = 'http://localhost:3000/'
    ALLOWED_REDIRECT_HOSTS = ['localhost', '127.0.0.1']
else:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
    LOGIN_REDIRECT_URL = config('LOGIN_REDIRECT_URL', default='https://yourdomain.com/')
    LOGOUT_REDIRECT_URL = config('LOGOUT_REDIRECT_URL', default='https://yourdomain.com/')
    ALLOWED_REDIRECT_HOSTS = config(
        'ALLOWED_REDIRECT_HOSTS',
        default='yourdomain.com',
        cast=lambda v: [s.strip() for s in v.split(',')]
    )