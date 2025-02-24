from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.utils.jwt_handler import generate_token
from app.utils.validators import is_valid_email, is_strong_password
from flask_login import login_user

def register_user(name, email, password, phone, location, user_type):
    if not is_valid_email(email):
        return None, 'Invalid email format'
    if not is_strong_password(password):
        return None, 'Password is not strong enough'
    if User.query.filter_by(email=email).first():
        return None, 'Email already registered'

    hashed_password = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed_password, phone=phone, location=location, user_type=user_type)
    user.save()
    return user, None

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        token = generate_token(user.id)
        return token, None
    return None, 'Invalid credentials'

def get_user_by_id(user_id):
    return User.query.get(user_id)

def login_user_service(form):
    user = User.query.filter_by(email=form.email.data).first()
    if user and check_password_hash(user.password, form.password.data):
        login_user(user)
        return user, None
    return None, 'Invalid email or password'