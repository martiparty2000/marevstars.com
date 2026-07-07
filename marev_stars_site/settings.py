from pathlib import Path
import os

# 1. Core Directory Setup
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Security Configurations
# Настройки за статични файлове
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
SECRET_KEY = 'django-insecure-marev-stars-super-secret-key-12345'
DEBUG = True
ALLOWED_HOSTS = ['*']
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 3. Application Definitions
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'team.apps.TeamConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'marev_stars_site.urls'

# Updated Templates to include your root 'templates' folder
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
                # Keep this if you have a custom context processor for pending_count
                'team.context_processors.pending_approvals_processor', 
            ],
        },
    },
]

WSGI_APPLICATION = 'marev_stars_site.wsgi.application'

# 4. Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 5. User Profile Strategy
AUTH_USER_MODEL = 'team.UserProfile'

# 6. Static Asset Locations
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'team/static',
]
# Path where static files are collected for production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 7. Login/Logout redirects (Optional but recommended)
LOGIN_REDIRECT_URL = 'team:home'
LOGOUT_REDIRECT_URL = 'team:home'
LOGIN_URL = 'team:login'