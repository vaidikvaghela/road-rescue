import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-roadrescue-secret-key-change-in-production-2024')

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'accounts',
    'services',
    'emergency',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'roadrescue.urls'

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
                'roadrescue.context_processors.google_maps',
            ],
        },
    },
]

WSGI_APPLICATION = 'roadrescue.wsgi.application'

# Database Configuration
# Works out of the box locally (SQLite), on Vercel Build (Dummy if sqlite is missing), and Production (PostgreSQL/MySQL)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
            )
        }
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
        }
    except ImportError:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.dummy',
            }
        }
else:
    try:
        import sqlite3
        HAS_SQLITE = True
    except ImportError:
        HAS_SQLITE = False

    if HAS_SQLITE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    else:
        # Fallback to dummy if sqlite3 is not available in the runtime/build environment
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.dummy',
            }
        }


AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

SPECTACULAR_SETTINGS = {
    'TITLE': 'RoadRescue API',
    'DESCRIPTION': 'Vehicle Breakdown Portal REST API',
    'VERSION': '1.0.0',
}

JAZZMIN_SETTINGS = {
    "site_title": "RoadRescue Admin",
    "site_header": "RoadRescue",
    "site_brand": "RoadRescue Portal",
    "welcome_sign": "Welcome to RoadRescue Admin Panel",
    "copyright": "RoadRescue Vehicle Breakdown Portal",
    "search_model": ["accounts.User", "services.ServiceProvider", "emergency.EmergencyRequest"],
    "topmenu_links": [
        {"name": "Home",        "url": "admin:index"},
        {"name": "View Portal", "url": "/",          "new_window": True},
        {"name": "API Docs",    "url": "/api/docs/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "accounts.User":               "fas fa-user",
        "services.ServiceProvider":    "fas fa-wrench",
        "services.ServiceType":        "fas fa-list",
        "services.Review":             "fas fa-star",
        "emergency.EmergencyRequest":  "fas fa-exclamation-triangle",
        "emergency.Dispatch":          "fas fa-truck",
        "core.ContactMessage":         "fas fa-envelope",
    },
    "default_icon_parents":  "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "brand_colour":   "navbar-orange",
    "accent":         "accent-orange",
    "navbar":         "navbar-dark",
    "sidebar":        "sidebar-dark-orange",
    "theme":          "darkly",
    "dark_mode_theme":"darkly",
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Razorpay Configuration
RAZORPAY_KEY_ID     = os.environ.get('RAZORPAY_KEY_ID',     'rzp_test_Soqq4UkckSJLCq')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'OK65IPQaBMMkVc2aQ2cTObkI')

# Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY')

# Web Push Notifications (VAPID)
VAPID_PRIVATE_KEY = "_TIlkCd8tmikmgBoXIaXn2FZj4GdrsIF4SavpHLKm7U"
VAPID_PUBLIC_KEY = "BBci4T7wRVT4igB5zDvcKem5hjvMO5k_r0kpOR4VJdWChDikPM7HqbF9E6i5MnSrqenxt6-w6hlcfbgmnXaS18U"
VAPID_ADMIN_EMAIL = "mailto:admin@roadrescue.com"

