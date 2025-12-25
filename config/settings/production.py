from .base import *
import os
from urllib.parse import urlparse

from .base import *

DEBUG = False

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.CanonicalDomainMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ALLOWED_HOSTS = [
    "theuraniumcore.com",
    "www.theuraniumcore.com",
    ".railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://theuraniumcore.com",
    "https://www.theuraniumcore.com",
]

# Typical for canonical domain redirects, etc.
SECURE_SSL_REDIRECT = True

# --- Database: DATABASE_URL ---
# Requires: pip install dj-database-url
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}
