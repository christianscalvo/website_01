from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# Local DB (what you already had)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# In local dev, CSRF trusted origins is usually not needed unless you're doing HTTPS locally.
CSRF_TRUSTED_ORIGINS = []
