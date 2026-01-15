import os

"""
Environment configuration for the application.
Values are loaded at startup from OS environment variables.
"""

def read_env(var_name: str, default=None):
    return os.environ.get(var_name, default)

def ensure_env_present(value, name: str):
    if not value:
        raise RuntimeError(f"Required environment variable missing: {name}")

DATABASE_URL = read_env("DATABASE_URL")
WEBHOOK_SECRET = read_env("WEBHOOK_SECRET")
LOG_LEVEL = read_env("LOG_LEVEL", "INFO").upper()

ensure_env_present(DATABASE_URL, "DATABASE_URL")
