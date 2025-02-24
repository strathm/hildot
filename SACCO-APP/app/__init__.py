from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

# Initialize Flask Extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """Factory function to create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Flask-Login Configuration
    login_manager.login_view = "login"  # Adjusted for single routes.py structure
    login_manager.login_message_category = "info"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Routes from a single routes.py
    from app.routes import bp  # Import blueprint from a single routes.py file

    app.register_blueprint(bp)

    # Create Database Tables if not existing
    with app.app_context():
        db.create_all()

    return app
