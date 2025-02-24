import re
from flask import current_app


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    pattern = r'^\+?[0-9]{10,15}$'
    return re.match(pattern, phone) is not None


def is_strong_password(password):
    min_length = 8
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()-_=+[]{};:,.<>?/\|' for c in password)
    
    return len(password) >= min_length and has_upper and has_lower and has_digit and has_special


def is_valid_image(filename):
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def is_valid_location(location):
    return isinstance(location, str) and len(location.strip()) > 0


def is_valid_name(name):
    return isinstance(name, str) and len(name.strip()) > 1


import re

def validate_email(email):
    """
    Validates an email address using a simple regex pattern.

    :param email: The email address to validate.
    :return: True if valid, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None
