import logging
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    _env_file = Path(__file__).resolve().parent / ".env"
    if _env_file.is_file():
        load_dotenv(_env_file)


def _get_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


# Number of emails to fetch from Gmail (override with NUM_EMAILS_TO_FETCH)
NUM_EMAILS_TO_FETCH = _get_int("NUM_EMAILS_TO_FETCH", 10)

LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(levelname)s - %(message)s",
}

# Production DB — set DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT (GitHub: repository secrets + env in workflow)
PROD_DB_CONFIG = {
    "host": os.environ.get("DB_HOST", ""),
    "user": os.environ.get("DB_USER", ""),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", ""),
    "port": _get_int("DB_PORT", 3306),
}

# Test DB — optional overrides for CI or non-default local MySQL
TEST_DB_CONFIG = {
    "host": os.environ.get("TEST_DB_HOST", "localhost"),
    "user": os.environ.get("TEST_DB_USER", "llhub"),
    "password": os.environ.get("TEST_DB_PASSWORD", "llhub"),
    "database": os.environ.get("TEST_DB_NAME", "llhub"),
    "port": _get_int("TEST_DB_PORT", 3306),
}

DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
