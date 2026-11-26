"""
Réglages de Global Service Congo.

Les valeurs sensibles ou qui changent entre le local et la production
(clé secrète, DEBUG, base de données, domaines) sont lues depuis les
variables d'environnement, via django-environ.
En local : fichier .env. Sur Render : tableau de bord.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Valeur par défaut sûre : si DEBUG n'est pas défini, il vaut False.
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")


# --- Sécurité de base -------------------------------------------------------

# Pas de valeur par défaut : si la clé manque, Django refuse de démarrer.
# C'est voulu, pour ne jamais tourner en production avec une clé connue.
SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])


# --- Applications -----------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Nos applications
    "core",
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


# --- Base de données --------------------------------------------------------

# En local : SQLite par défaut. En production : DATABASE_URL (Neon) dans Render.
# .as_posix() remplace les "\" de Windows par des "/" dans le chemin.
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}",
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Modèle utilisateur personnalisé : activé à l'étape 1c, AVANT le premier migrate.
# AUTH_USER_MODEL = "accounts.User"


# --- Mots de passe ----------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Langue et fuseau horaire -----------------------------------------------

LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True  # dates stockées en UTC, affichées à l'heure de Kinshasa


# --- Fichiers statiques et uploads ------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # rempli par collectstatic au déploiement

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# --- Règles métier ----------------------------------------------------------

# Commission prélevée sur le montant versé au prestataire (en %).
PLATFORM_FEE_PERCENT = env.int("PLATFORM_FEE_PERCENT", default=10)

# Adresse de l'administration : on évite « admin/ », que tous les robots testent.
ADMIN_URL = env("ADMIN_URL", default="admin/")


# --- Sécurité en production -------------------------------------------------

if not DEBUG:
    # Render place un proxy devant l'application : on lui fait confiance pour savoir si la requête était en HTTPS.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True  # cookie de session envoyé uniquement en HTTPS
    CSRF_COOKIE_SECURE = True
    # HSTS : le navigateur refusera le HTTP pour ce site.
    # On commence à 1 heure et on augmentera quand tout sera stable.
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True