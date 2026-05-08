import os

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-key-do-not-use-in-production-aB3xK9mQ2pL7",
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Development ortamında rate limiting devre dışı
RATELIMIT_ENABLE = False
