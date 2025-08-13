"""
Django settings for config project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# -------------------------------------------------
# Paths & .env
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# -------------------------------------------------
# Core
# -------------------------------------------------
SECRET_KEY = 'django-insecure-x&mdo=c0j0h0-yr3pehk!8&)pqo220su-bz(bf^ei4o*0)2%$l'
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".ngrok-free.app"]
CSRF_TRUSTED_ORIGINS = ["https://*.ngrok-free.app"]

# -------------------------------------------------
# Applications
# -------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceiros
    "tailwind",
    "django_browser_reload",
    "widget_tweaks",

    # App do projeto
    "theme.apps.ThemeConfig",
    "store.apps.StoreConfig",

    # (axes) Remova estas 2 linhas se não quiser usar django-axes
    "axes",
]

# -------------------------------------------------
# Middleware (ordem IMPORTA)
# -------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Sempre antes de AuthenticationMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",

    # Locale (opcional)
    "django.middleware.locale.LocaleMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    # Necessários para admin/login
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # (axes) remova se não for usar
    "axes.middleware.AxesMiddleware",

    # Live reload
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]


ROOT_URLCONF = "config.urls"

# -------------------------------------------------
# Templates
# -------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.carrinho_total",
                "store.context_processors.categorias_context",
                "store.context_processors.favoritos_ids",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -------------------------------------------------
# Database
# -------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------
# Auth / Passwords
# -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Backends de autenticação
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    # (axes) Ative se usar o django-axes
    "axes.backends.AxesStandaloneBackend",
]

LOGIN_URL = "/login/"

# -------------------------------------------------
# I18N / TZ
# -------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------
# Static & Media
# -------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# -------------------------------------------------
# Tailwind / Dev
# -------------------------------------------------
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = ["127.0.0.1"]
NPM_BIN_PATH = r"C:/Program Files/nodejs/npm.cmd"

# -------------------------------------------------
# E-mail
# -------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@seusite.com"

# -------------------------------------------------
# Integrações
# -------------------------------------------------
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN_TEST", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://127.0.0.1:8000")

RECAPTCHA_SITE_KEY = "6Lf-gpwrAAAAAFFYbf2wq560wRlkvneimQIgIE75"
RECAPTCHA_SECRET_KEY = "6Lf-gpwrAAAAAOc-Xx1C1sk2uiNvKopOLnC8XmKA"

# -------------------------------------------------
# django-axes (se ativo)
# -------------------------------------------------
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # em horas
