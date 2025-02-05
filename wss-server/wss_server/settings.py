from pathlib import Path
import os
from . import key_define

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = key_define.DJANGO_SECRET_KEY

DEBUG = False
IS_MAINTENANCE = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'channels',
    'daphne',
    'rest_framework',
    'django_user_agents',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.devices',
    'apps.api_websocket',
    'apps.record',
    'apps.system',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

USER_AGENTS_CACHE = 'default'

WSGI_APPLICATION = 'wss_server.wsgi.application'
ASGI_APPLICATION = 'wss_server.asgi.application'

ROOT_URLCONF = 'wss_server.urls'

LOGIN_URL = '/accounts/login/'
AUTH_USER_MODEL = 'accounts.Users'
AUTHENTICATION_BACKENDS = (
    'apps.accounts.authenticate.LoginBackend',
)

SILENCED_SYSTEM_CHECKS = ['auth.W004']

ADMINS = key_define.ADMINS
SEND_BROKEN_LINK_EMAILS = True
MANAGERS = ADMINS

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = key_define.DATABASE_INFO

CACHES = key_define.CACHES

CHANNEL_LAYERS = key_define.CHANNEL_LAYERS


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / 'static', ]
else:
    STATIC_ROOT = BASE_DIR / 'static'


# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# logfile
log_path = BASE_DIR / 'logs'
if not os.path.exists(log_path):
    os.makedirs("logs")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = key_define.EMAIL_BACKEND
EMAIL_HOST = key_define.EMAIL_HOST
EMAIL_PORT = key_define.EMAIL_PORT
EMAIL_HOST_USER = key_define.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = key_define.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = key_define.EMAIL_USE_TLS
EMAIL_SUBJECT_PREFIX = key_define.EMAIL_SUBJECT_PREFIX
EMAIL_USE_SSL = key_define.EMAIL_USE_SSL
DEFAULT_FROM_EMAIL = key_define.EMAIL_HOST_USER

GITHUB_CLIENT_ID = key_define.GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET = key_define.GITHUB_CLIENT_SECRET

GOOGLE_CLIENT_ID = key_define.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = key_define.GOOGLE_CLIENT_SECRET

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
