"""
PNG Compliance Hub 2026
Django Settings - Development & Production combined
"""

from pathlib import Path
from decouple import config

# ─── Base Paths ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='django-insecure-png-compliance-hub-2026-dev-key-change-in-prod')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

CSRF_USE_SESSIONS = True
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
CSRF_COOKIE_AGE = 86400 * 30
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']

# ─── Application Definition ──────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'django_htmx',

    # PNG Compliance Hub Apps
    'core',
    'accounts',
    'dashboard',
    'gst',
    'swt',
    'sbt',
    'reports',
    'tax_guide',
    
    # 3rd Party
    'markdownx',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.ImpersonationMiddleware',
    'core.middleware.RoleSeparationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',  # HTMX request detection
]

ROOT_URLCONF = 'compliance_hub.urls'

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
                'core.context_processors.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'compliance_hub.wsgi.application'

# ─── Database ─────────────────────────────────────────────────────────────────
# Development: SQLite | Production: switch to PostgreSQL via DATABASE_URL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── Authentication ──────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'auth.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalization ────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Pacific/Port_Moresby'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# ─── Static Files ────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── PNG Compliance Hub - App Settings ───────────────────────────────────────
GST_RATE = 0.10  # 10% standard rate
SBT_THRESHOLD = 250_000  # SBT only for turnover < K250,000
SBT_FLAT_FEE_THRESHOLD = 50_000  # Below K50k → K400 flat
SBT_FLAT_FEE_AMOUNT = 400
SBT_RATE = 0.02  # 2% for K50k–K250k turnover

# SWT 2026 Resident Progressive Brackets: (upper_limit, rate)
# None = no upper limit (top bracket)
SWT_RESIDENT_BRACKETS = [
    (20_000, 0.22),
    (33_000, 0.30),
    (70_000, 0.35),
    (250_000, 0.40),
    (None, 0.42),
]
