from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, decode_jwt
from cryptography.fernet import Fernet
import os

# Ensure the encryption key is securely handled
encryption_key = os.environ.get("ENCRYPTION_KEY")
if not encryption_key:
    raise ValueError("ENCRYPTION_KEY environment variable is not set!")
cipher_suite = Fernet(encryption_key)

# Password hashing
def hash_password(password):
    """
    Hash a plaintext password.
    """
    return generate_password_hash(password)

def verify_password(password, hashed_password):
    """
    Verify a plaintext password against a hashed password.
    """
    return check_password_hash(hashed_password, password)

# Token management
def create_jwt_token(user_id, role):
    """
    Create a JWT token for a user.
    """
    return create_access_token(identity={"id": user_id, "role": role})

def decode_jwt_token(token):
    """
    Decode a JWT token to extract user information.
    """
    try:
        return decode_jwt(token)
    except Exception as e:
        raise ValueError("Invalid or expired JWT token") from e

# Data encryption
def encrypt_data(data):
    """
    Encrypt sensitive data.
    """
    try:
        return cipher_suite.encrypt(data.encode()).decode()
    except Exception as e:
        raise ValueError("Error encrypting data") from e

def decrypt_data(encrypted_data):
    """
    Decrypt sensitive data.
    """
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        raise ValueError("Error decrypting data") from e
