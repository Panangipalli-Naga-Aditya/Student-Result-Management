import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
BASE = os.path.abspath(os.path.dirname(__file__))

# DATA_DIR can point to a persistent disk/volume on your hosting provider.
# For local use, it defaults to the project directory.
DATA_DIR = os.path.abspath(os.environ.get("DATA_DIR", BASE))
os.makedirs(DATA_DIR, exist_ok=True)


def _database_url():
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        return "sqlite:///" + os.path.join(DATA_DIR, "physics_hub.db")
    # Some hosts still provide the old postgres:// scheme.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.abspath(os.environ.get("UPLOAD_FOLDER", os.path.join(DATA_DIR, "uploads")))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", 20)) * 1024 * 1024

    # Keep authentication valid across browser restarts for 30 days.
    # This does not delete the account or its database records when it expires.
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = os.environ.get("REMEMBER_COOKIE_SECURE", "0") == "1"
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
