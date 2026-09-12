"""
Django settings for AUL project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# BASE_DIR указывает на папку backend/
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Включаем директорию apps в sys.path для удобного импорта приложений
import sys

# Включаем директорию apps в sys.path для удобного импорта приложений
import sys
sys.path.insert(0, str(BASE_DIR / 'apps'))

# Секретный ключ
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-aul-development-key-change-in-production'
)

# VAPID настройки для Web Push
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
VAPID_CLAIMS_EMAIL = os.getenv('VAPID_CLAIMS_EMAIL')

# Режим отладки
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Настройка CSRF доверенных доменов для GitHub Codespaces
CSRF_TRUSTED_ORIGINS = [
    "https://aooool-production.up.railway.app",
    "https://verbose-space-spoon-jr6v9rxx4x53966-8000.app.github.dev",
    "https://localhost:8000",
    "http://localhost:8000",
]


# Подключенные приложения
INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Приложения проекта AUL
    'apps.users',
    'apps.notifications',
    'apps.trips',
    'apps.ads',
    'apps.directory',
    'apps.weather',
]

# Кастомная модель пользователя
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aul_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aul_project.wsgi.application'


# База данных
# Локально используется SQLite, на Railway — PostgreSQL через DATABASE_URL.
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Валидаторы паролей
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


# Языковые и временные настройки
LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_TZ = True


# Статические файлы (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Медиа файлы (загружаемые пользователем фотографии)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Тип первичных ключей по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Авторизация и редиректы
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'login'

# Кэширование (локальная память для разработки / быстрого ответа)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'aul-cache-local',
    }
}

# География и настройки погоды AUL (село Кабанбай, Жетысуская / Алматинская область)
WEATHER_LATITUDE = float(os.getenv('WEATHER_LATITUDE', '45.8344'))
WEATHER_LONGITUDE = float(os.getenv('WEATHER_LONGITUDE', '80.6067'))
WEATHER_LOCATION_NAME = os.getenv('WEATHER_LOCATION_NAME', 'Кабанбай')
WEATHER_CACHE_TIMEOUT = int(os.getenv('WEATHER_CACHE_TIMEOUT', '600'))  # 10 минут


# Production-настройки для Railway
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
