from .settings import *

# Allow Django's test client hostname during tests only.
ALLOWED_HOSTS = [*ALLOWED_HOSTS, "testserver"]

# Always use the in-memory email backend for tests.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"