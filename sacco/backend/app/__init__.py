from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=None):
    """
    Create and configure the Flask application.

    Args:
        config_class (str): Configuration class path (default is set to the development environment).

    Returns:
        Flask app instance.
    """
    # Default to 'DevelopmentConfig' if no config is specified
    if config_class is None:
        config_class = os.getenv("FLASK_CONFIG", "app.config.DevelopmentConfig")

    app = Flask(__name__)

    try:
        # Load configuration from the specified class
        app.config.from_object(config_class)
    except ImportError as e:
        raise ImportError(f"Could not import configuration class '{config_class}': {e}")

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)  # Enable CORS for cross-origin requests

    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.member import member_bp
    from app.routes.transaction import transaction_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(member_bp, url_prefix="/api/member")
    app.register_blueprint(transaction_bp, url_prefix="/api/transactions")

    # Custom error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"message": "Resource not found", "status": 404}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"message": "An internal server error occurred", "status": 500}, 500

    return app
