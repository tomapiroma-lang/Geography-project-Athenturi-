import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
ON_VERCEL = bool(os.getenv("VERCEL"))


def _database_url():
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url.replace("postgres://", "postgresql://", 1)
    folder = Path("/tmp") if ON_VERCEL else BASE_DIR / "instance"
    folder.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{folder / 'athenturi.db'}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ON_VERCEL
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14
    MAX_CONTENT_LENGTH = 64 * 1024

    SITE_NAME = "ათენტური"
    SITE_URL = os.getenv("SITE_URL", "http://localhost:5000").rstrip("/")
    SITE_EMAIL = os.getenv("SITE_EMAIL", "hello@example.com")
    SITE_PHONE = os.getenv("SITE_PHONE", "+995 5XX XX XX XX")
    ADMIN_EMAILS = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}

    MAIL_HOST = os.getenv("MAIL_HOST", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USER = os.getenv("MAIL_USER", "")
    MAIL_PASS = os.getenv("MAIL_PASS", "")
    MAIL_TO = os.getenv("MAIL_TO", "") or os.getenv("SITE_EMAIL", "")
