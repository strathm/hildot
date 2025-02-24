import re

def validate_email(email):
    """
    Validate email format.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def validate_phone_number(phone_number):
    """
    Validate phone number format (e.g., Kenyan phone numbers).
    """
    # Allow optional starting '+' for international format, e.g., +254xxxxxxxxx
    pattern = r"^(?:\+254|254)\d{9}$"  # Formats for Kenyan phone numbers: 254xxxxxxxxx or +254xxxxxxxxx
    return bool(re.match(pattern, phone_number))

def validate_password(password):
    """
    Validate password strength (minimum 8 characters, at least one number and one special character).
    """
    if len(password) < 8:
        return False
    if not re.search(r"[0-9]", password):  # Must contain at least one digit
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Must contain at least one special character
        return False
    return True

def validate_positive_number(value):
    """
    Validate that a number is positive.
    """
    try:
        # Check if the value can be converted to a float and is positive
        return float(value) > 0
    except (ValueError, TypeError):
        # If it's not a number, return False
        return False
