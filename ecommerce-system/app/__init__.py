from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_mail import Mail
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()

# For image uploads
images = UploadSet('images', IMAGES)

# Define user_loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import User model
    return User.query.get(int(user_id))  # Fetch the user by ID

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['UPLOADED_IMAGES_DEST'] = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email configuration (update with actual SMTP settings)
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@example.com'
    app.config['MAIL_PASSWORD'] = 'your_email_password'
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@example.com'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Configure Flask-Uploads
    configure_uploads(app, images)

    # Set login configuration
    login_manager.login_view = 'main.login'  # Update this to your login route
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .models import User
    import click
    from flask.cli import with_appcontext
    from werkzeug.security import generate_password_hash

    # Add the CLI command for creating admin or seller users
    @click.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    @click.argument('county')
    @click.argument('subcounty')
    @click.argument('street')
    @click.option('--role', default='admin', type=click.Choice(['admin', 'seller']), help="Specify role: 'admin' for Shop Owner, 'seller' for limited access.")
    @with_appcontext
    def create_admin(username, email, password, county, subcounty, street, role):
        """Creates a new admin (Shop Owner) or Seller user."""

        # Check if the email or username already exists
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            click.echo(f"User with email {email} or username {username} already exists.")
            return
        
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create the new user with the specified role
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            county=county,
            subcounty=subcounty,
            street=street,
            role=role  # Set the role directly instead of using is_admin and is_seller
        )
        
        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()
        
        click.echo(f"{role.capitalize()} user '{username}' created successfully.")

    # Register the command to the app
    app.cli.add_command(create_admin)

    return app
