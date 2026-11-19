from .dev import *  # noqa: F401,F403
from .base import env

# The test database is created and migrated as the owner role.
# tests/conftest.py then reconnects as the restricted runtime role
# (DATABASE_URL), so every test runs with production privileges.
DATABASES = {"default": env.db("MIGRATION_DATABASE_URL")}
RUNTIME_DATABASE = env.db("DATABASE_URL")
DB_RUNTIME_ROLE = RUNTIME_DATABASE["USER"]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
