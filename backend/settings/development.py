"""Local development: SQLite and optional debugging tools."""
from .base import *

DEBUG = True
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
