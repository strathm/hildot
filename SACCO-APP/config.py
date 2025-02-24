import os

class Config:
    # ---------------------- GENERAL CONFIGURATIONS ----------------------
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # Secret key for session management
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')  # Set environment (development/production)
    DEBUG = True if FLASK_ENV == 'development' else False  # Enable debug mode in development
    
    # ---------------------- DATABASE CONFIGURATIONS ----------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance reasons
    SQLALCHEMY_ECHO = True if FLASK_ENV == 'development' else False  # Log SQL queries in development mode

    # Database URI (use SQLite for development, Postgres for production, etc.)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sacco.db')

    # ---------------------- M-PESA INTEGRATION ----------------------
    MPESA_API_KEY = os.getenv('MPESA_API_KEY', 'your-mpesa-api-key')  # API key for M-Pesa
    MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', 'your-shortcode')  # M-Pesa shortcode for payment gateway
    MPESA_LIPA_NNN = os.getenv('MPESA_LIPA_NNN', 'lipana-na-mpesa')  # M-Pesa Lipana Na M-Pesa shortcode for payments
    MPESA_SHORTCODE_PASSKEY = os.getenv('MPESA_SHORTCODE_PASSKEY', 'your-passkey')  # Passkey for M-Pesa API
    MPESA_LIPA_NNN_URL = os.getenv('MPESA_LIPA_NNN_URL', 'https://api.safaricom.co.ke/...')
    MPESA_LIPA_NNN_SHORTCODE = os.getenv('MPESA_LIPA_NNN_SHORTCODE', 'shortcode-lipa')  # M-Pesa short code for payments

    # ---------------------- MAIL CONFIGURATIONS ----------------------
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')  # Email server to use for sending email notifications
    MAIL_PORT = os.getenv('MAIL_PORT', 587)  # Port for the email server
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)  # Whether to use TLS encryption
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', False)  # Whether to use SSL encryption
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')  # Email address for sending emails
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your-email-password')  # Password for the email account
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@yourdomain.com')  # Default sender for emails

    # ---------------------- SECURITY CONFIGURATIONS ----------------------
    # Rate limiter settings
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100/hour')  # Max number of requests per hour

    # ---------------------- CELERY CONFIGURATIONS (for background tasks) ----------------------
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')  # URL for the message broker (e.g., Redis)
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')  # Backend for storing results
    
    # ---------------------- LOGGING CONFIGURATIONS ----------------------
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOGGING_FORMAT = os.getenv('LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log format
    LOGGING_FILE = os.getenv('LOGGING_FILE', 'app.log')  # Log file location

    # ---------------------- PAYMENT CONFIGURATIONS ----------------------
    # Use environment variables to manage payment provider configurations
    PAYMENT_PROVIDER = os.getenv('PAYMENT_PROVIDER', 'MPESA')  # Default payment provider
    PAYMENT_GATEWAY_URL = os.getenv('PAYMENT_GATEWAY_URL', 'https://api.safaricom.co.ke/')

    # ---------------------- JWT CONFIGURATIONS ----------------------
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')  # Secret key for JWT tokens
    JWT_ACCESS_TOKEN_EXPIRES = os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)  # Expiry time for access token (in seconds)
    
    # ---------------------- CACHE CONFIGURATIONS ----------------------
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # Cache type (simple, redis, etc.)
    CACHE_DEFAULT_TIMEOUT = os.getenv('CACHE_DEFAULT_TIMEOUT', 300)  # Default timeout for cache (in seconds)
    
    # ---------------------- PAYMENT TRANSACTION LOGGING ----------------------
    ENABLE_PAYMENT_LOGGING = os.getenv('ENABLE_PAYMENT_LOGGING', True)  # Enable logging for payments made
    
    # ---------------------- ADMIN CONFIGURATIONS ----------------------
    ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', 'admin@example.com')  # List of admin emails for special permissions or monitoring

    # ---------------------- OTHERS ----------------------
    MAX_FILE_SIZE = os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024)  # Max file upload size (default is 10MB)
