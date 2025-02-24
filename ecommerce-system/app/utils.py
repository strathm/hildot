import os
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, current_app
from flask_mail import Message
from PIL import Image
from datetime import datetime

# Password Hashing
def hash_password(password):
    """Hash a plaintext password."""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Check a hashed password against a plaintext password."""
    return check_password_hash(hashed_password, password)

# Image Handling
def save_image(uploaded_file, folder='static/uploads', output_size=(300, 300)):
    """
    Save an uploaded image to the specified folder with resizing.
    :param uploaded_file: The uploaded file (from a form)
    :param folder: Folder to save the image
    :param output_size: Tuple for resizing the image (width, height)
    :return: Filename of the saved image
    """
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(uploaded_file.filename)
    filename = random_hex + file_ext
    file_path = os.path.join(current_app.root_path, folder, filename)

    # Resize and save the image
    img = Image.open(uploaded_file)
    img.thumbnail(output_size)
    img.save(file_path)

    return filename

# Inventory Check
def get_out_of_stock_products(products):
    """
    Get a list of out-of-stock products.
    :param products: List of product objects
    :return: List of out-of-stock product names
    """
    return [product for product in products if product.quantity <= 0]

def low_stock_alert(products, threshold=5):
    """
    Get a list of products with low stock.
    :param products: List of product objects
    :param threshold: Quantity threshold for low stock
    :return: List of low-stock product names
    """
    return [product for product in products if product.quantity > 0 and product.quantity <= threshold]

# Email Notifications
def send_email(subject, recipient, body, mail):
    """
    Send an email using Flask-Mail.
    :param subject: Email subject
    :param recipient: Recipient's email address
    :param body: Email body
    :param mail: Flask-Mail object
    """
    msg = Message(subject, recipients=[recipient], body=body)
    mail.send(msg)

def send_admin_alert(product_name, admin_email, mail):
    """
    Notify admin about a low-stock or out-of-stock product.
    :param product_name: Name of the product
    :param admin_email: Admin's email address
    :param mail: Flask-Mail object
    """
    subject = "Stock Alert: Action Required"
    body = f"The product '{product_name}' is either out of stock or running low. Please restock."
    send_email(subject, admin_email, body, mail)

# Date and Time Formatting
def format_datetime(dt, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Format a datetime object into a string.
    :param dt: Datetime object
    :param fmt: Format string
    :return: Formatted date string
    """
    return dt.strftime(fmt)

def human_readable_date(dt):
    """
    Convert a datetime to a human-readable date string.
    :param dt: Datetime object
    :return: Human-readable date string
    """
    return dt.strftime("%B %d, %Y")

# Product Filtering
def filter_products_by_category(products, category_id):
    """
    Filter a list of products by category.
    :param products: List of product objects
    :param category_id: Category ID to filter by
    :return: Filtered list of products
    """
    return [product for product in products if product.category_id == category_id]

def search_products(products, query):
    """
    Search for products by name or description.
    :param products: List of product objects
    :param query: Search query string
    :return: List of matching products
    """
    query = query.lower()
    return [
        product for product in products
        if query in product.name.lower() or (product.description and query in product.description.lower())
    ]

# Admin Utility
def add_admin(username, email, password, db, User):
    """
    Add a new admin user.
    :param username: Admin username
    :param email: Admin email
    :param password: Admin password
    :param db: Database instance
    :param User: User model
    """
    hashed_password = hash_password(password)
    admin = User(username=username, email=email, password=hashed_password, is_admin=True)
    db.session.add(admin)
    db.session.commit()

# File and Path Utilities
def create_folder(folder_path):
    """
    Create a folder if it doesn't exist.
    :param folder_path: Path of the folder to create
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Audit Logs
def log_action(action, user_id, db, AuditLog):
    """
    Record an action in the audit log.
    :param action: Action description
    :param user_id: ID of the user performing the action
    :param db: Database instance
    :param AuditLog: AuditLog model
    """
    log = AuditLog(action=action, user_id=user_id)
    db.session.add(log)
    db.session.commit()

# Cart Utilities
def calculate_cart_total(cart_items):
    """
    Calculate the total cost of items in a cart.
    :param cart_items: List of cart item objects
    :return: Total price
    """
    return sum(item.quantity * item.product.price for item in cart_items)

# Feedback Utilities
def average_product_rating(feedback_list):
    """
    Calculate the average rating for a product.
    :param feedback_list: List of feedback objects
    :return: Average rating (float)
    """
    ratings = [feedback.rating for feedback in feedback_list if feedback.rating]
    return sum(ratings) / len(ratings) if ratings else 0.0
import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image):
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        filepath = os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], filename)
        image.save(filepath)
        return filename
    return None
