import os

class Config:
    # General Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")  # Replace with a secure key
    DEBUG = os.getenv("DEBUG", False)
    TESTING = os.getenv("TESTING", False)

    # Database configuration (MSSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://username:password@server_address/db_name?driver=ODBC+Driver+17+for+SQL+Server"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications for performance
    SQLALCHEMY_POOL_SIZE = 10  # Set database connection pool size
    SQLALCHEMY_POOL_TIMEOUT = 30  # Set pool timeout

    # JWT configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-jwt-secret-key")  # Replace with a secure key
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Token expires in 1 hour (3600 seconds)

    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # Allow all origins for now, restrict in production
    
    # Redis configuration (for caching or session management)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # M-Pesa API Configuration
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "your-mpesa-consumer-key")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "your-mpesa-consumer-secret")
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "your-mpesa-shortcode")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "your-mpesa-passkey")
    MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")  # 'sandbox' or 'production'

    # Email Configuration (for notifications, optional)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = os.getenv("MAIL_PORT", 587)
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", True)
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your-email@example.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-email-password")

    # Logging Configuration
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")  # Default log level
    LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOGGING_FILE = os.getenv("LOGGING_FILE", "app.log")

    # File upload settings
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/")
    MAX_CONTENT_LENGTH = os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)  # Max file size 16MB

    # Security settings
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", True)  # Ensures cookies are sent only over HTTPS in production
    REMEMBER_COOKIE_DURATION = os.getenv("REMEMBER_COOKIE_DURATION", 60 * 60 * 24 * 7)  # 1 week

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries for debugging
    LOGGING_LEVEL = "DEBUG"
    LOGGING_FILE = "development.log"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")  # Use a different Redis database for development

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://your-production-domain.com")
    LOGGING_LEVEL = "WARNING"
    LOGGING_FILE = "production.log"
    SQLALCHEMY_POOL_SIZE = 20  # Increase pool size for production environment
    SQLALCHEMY_POOL_TIMEOUT = 60  # Increase pool timeout for production
    REDIS_URL = os.getenv("REDIS_URL", "redis://production-redis-server:6379/0")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use in-memory database for tests
    JWT_ACCESS_TOKEN_EXPIRES = 300  # Short expiry for testing
    LOGGING_LEVEL = "DEBUG"
    LOGGING_FILE = "testing.log"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/2")  # Use a different Redis database for testing
