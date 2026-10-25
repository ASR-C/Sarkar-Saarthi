"""
Django settings for Sarkari Saathi (Government Form Guidance Platform).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Install PyMySQL as MySQLdb for MySQL/TiDB compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-fallback-key-sarkari-saathi')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'guides.apps.GuidesConfig',
    'wizard.apps.WizardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database Configuration: TiDB Cloud (MySQL-compatible) with fallback to SQLite
TIDB_HOST = os.getenv('TIDB_HOST', '').strip()
if TIDB_HOST:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('TIDB_DATABASE', 'sarkari_saathi'),
            'USER': os.getenv('TIDB_USER', 'root'),
            'PASSWORD': os.getenv('TIDB_PASSWORD', ''),
            'HOST': TIDB_HOST,
            'PORT': os.getenv('TIDB_PORT', '4000'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'ssl': {
                    'ca': os.getenv('TIDB_CA_PATH')
                } if os.getenv('TIDB_CA_PATH') else {'ssl_mode': 'REQUIRED'},
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Custom User Model
AUTH_USER_MODEL = 'accounts.User'


# Password Hashing: Argon2 as mandated by PRD
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिन्दी (Hindi)'),
    ('mwr', 'मारवाड़ी (Marwadi)'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# Static and Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Security & Cookie Settings
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Brevo Transactional Email Configuration
BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
BREVO_SENDER_EMAIL = os.getenv('BREVO_SENDER_EMAIL', 'noreply@sarkarisaathi.org')
BREVO_SENDER_NAME = os.getenv('BREVO_SENDER_NAME', 'Sarkari Saathi')

# Groq AI Assistant Configuration (Phase 2)
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
