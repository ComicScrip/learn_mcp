"""Réglages Django réduits au strict minimum pour l'exemple."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-only-not-secret"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "todos",
]

ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Les stats regroupent les tâches par jour : il faut savoir où « minuit » tombe.
USE_TZ = True
TIME_ZONE = "Europe/Paris"

# Pas d'auth pour garder l'exemple lisible (à NE PAS faire en prod).
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
}

# Le fichier HTML unique produit par `npm run build` dans ../frontend
MCP_APP_HTML = BASE_DIR.parent / "frontend" / "dist" / "mcp-app.html"
