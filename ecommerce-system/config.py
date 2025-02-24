import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if available)
load_dotenv()

class Config:
    """Base configuration with default settings."""
    
    # General Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    DEBUG = False
    TESTING = False

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF Protection (Enabled by Default)
    WTF_CSRF_ENABLED = True

    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ["true", "1", "yes"]
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in ["true", "1", "yes"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # File Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit

    # Caching Configuration
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")  # e.g., RedisCache, MemcachedCache
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))  # 5 minutes
    REDIS_URL = os.getenv("REDIS_URL", None)  # For Redis-based caching

    # Pagination Settings
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", 10))

    # Security Settings
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() in ["true", "1", "yes"]
    REMEMBER_COOKIE_SECURE = os.getenv("REMEMBER_COOKIE_SECURE", "true").lower() in ["true", "1", "yes"]
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = "Lax"  # Prevent CSRF attacks from other sites

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")

    # Payment Gateway Integrations
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", None)
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", None)
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", None)

    # Localization
    BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", "en")
    BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", "UTC")

    # Future Integrations (e.g., AI, Webhooks)
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", None)
    AI_API_KEY = os.getenv("AI_API_KEY", None)

class DevelopmentConfig(Config):
    """Configuration for development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "sqlite:///dev.db")

class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    MAIL_SUPPRESS_SEND = True  # Disable emails during tests
    SESSION_COOKIE_SECURE = False  # Allow HTTP in testing

class ProductionConfig(Config):
    """Configuration for production."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URL", "sqlite:///prod.db")
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

class StagingConfig(Config):
    """Configuration for staging."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("STAGING_DATABASE_URL", "sqlite:///staging.db")

# Config Mapping
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "staging": StagingConfig,
    "default": DevelopmentConfig
}
