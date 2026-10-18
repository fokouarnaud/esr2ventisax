"""Réglages du Carnet de stage. Les secrets viennent de webapp/.env (jamais versionné)."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
if not os.environ.get("CARNET_SANS_DOTENV"):  # les tests de déploiement contrôlent tout l'environnement
    load_dotenv(BASE_DIR / ".env")

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or (
    "dev-uniquement-ne-pas-utiliser-en-production" if DEBUG else None
)
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY manquant : le définir dans webapp/.env (voir DEPLOIEMENT.md).")
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")]

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "carnet",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
LOCALE_PATHS = [BASE_DIR / "locale"]  # traduction française des chaînes de django-unfold (A10)
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path(os.environ.get("CARNET_STATIC_ROOT", BASE_DIR / "staticfiles"))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Production : noms avec empreinte (carnet.3f9a1c….css) → le cache navigateur ne sert jamais une vieille version
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if DEBUG
                    else "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "carnet:note_rapide"

# Compte gratuit PythonAnywhere : 512 Mo pour tout (A33)
CARNET_DISQUE_TOTAL_MO = int(os.environ.get("CARNET_DISQUE_TOTAL_MO", "512"))
CARNET_SEUIL_ALERTE_DISQUE = 0.80

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    # HSTS court et limité à notre sous-domaine : pythonanywhere.com est partagé
    SECURE_HSTS_SECONDS = 86400
    SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]  # ni sous-domaines ni preload : domaine partagé



def _statique(chemin):
    """URL versionnée (empreinte) d'un fichier statique, résolue à la requête."""
    def url(request):
        from django.templatetags.static import static
        return static(chemin)
    return url


# Palette de ventisax.pythonanywhere.com (A11) : turquoise #68ddce / #0d665e, marine #0b2d46
UNFOLD = {
    "SITE_TITLE": "Carnet de stage",
    "SITE_HEADER": "Carnet de stage",
    "SITE_SUBHEADER": "Journal de terrain du rapport",
    "SITE_SYMBOL": "menu_book",
    "SITE_URL": "/carnet/note/",
    "SHOW_HISTORY": False,
    "SHOW_VIEW_ON_SITE": False,
    "BORDER_RADIUS": "12px",
    "DASHBOARD_CALLBACK": "carnet.tableau.dashboard_callback",
    "SITE_FAVICONS": [
        {"rel": "icon", "type": "image/svg+xml", "href": _statique("carnet/favicon.svg")},
    ],
    "STYLES": [
        _statique("carnet/css/polices.css"),
        _statique("carnet/css/admin.css"),
    ],
    "COLORS": {
        "base": {
            "50": "#f4f7f8", "100": "#e9eff1", "200": "#e1e7ea", "300": "#c9d6dc", "400": "#a7bac4",
            "500": "#71889a", "600": "#4a5d69", "700": "#2b4152", "800": "#16324a", "900": "#10283a",
            "950": "#0a1c28",
        },
        "primary": {
            "50": "#effcfa", "100": "#e3f4f1", "200": "#c3ece5", "300": "#8fe7dc", "400": "#68ddce",
            "500": "#36c2b0", "600": "#0d665e", "700": "#0b5750", "800": "#0e4a44", "900": "#0d3f3b",
            "950": "#052422",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}
