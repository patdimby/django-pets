"""Production configuration; provide secrets and database URL via environment."""
from .base import *

DEBUG = False
DATABASES = {"default": env.db("DATABASE_URL")}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
