from . import db
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Location fields (conditionally required for customers)
    county = db.Column(db.String(100))
    subcounty = db.Column(db.String(100))
    street = db.Column(db.String(200))

    # Role-based Access Control
    role = db.Column(db.String(20), nullable=False, default="customer")  # Can be "admin", "seller", or "customer"

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username} - Role: {self.role}>"

    def set_password(self, password):
        """Hashes and stores the user's password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifies if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

    def reset_password(self, new_password):
        """Resets the user's password."""
        self.set_password(new_password)

    @property
    def is_admin(self):
        """Check if the user is an admin (shop owner)."""
        return self.role.lower() == "admin"

    @property
    def is_seller(self):
        """Check if the user is a seller."""
        return self.role.lower() == "seller"

    @property
    def is_customer(self):
        """Check if the user is a regular customer."""
        return self.role.lower() == "customer"

    def validate_user(self):
        """
        Ensures that:
        - Customers must provide county, subcounty, and street.
        - Admins and sellers can leave those fields empty.
        """
        if self.is_customer and (not self.county or not self.subcounty or not self.street):
            raise ValueError("Customers must provide county, subcounty, and street.")

    def get_reset_token(self, expires_sec=3600):
        """Generates a secure token for password reset."""
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=3600):
        """Verifies the password reset token."""
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except:
            return None
        return User.query.filter_by(email=email).first()
# Product Model
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(255), nullable=True)  # Path to uploaded image
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f"<Product {self.name}>"
class SelectedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    document_number = db.Column(db.String(20), nullable=False)  # No unique=True
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_number = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)  # This will hold the full HTML version of the invoice/receipt
    is_paid = db.Column(db.Boolean, default=False)
    printed_at = db.Column(db.DateTime, default=datetime.utcnow)


class SoldItem(db.Model):
    __tablename__ = 'sold_items'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.Text, nullable=True)
    product_price = db.Column(db.Float, nullable=False)
    product_image = db.Column(db.String(255), nullable=True)  # Path to image at time of sale
    product_category_id = db.Column(db.Integer, nullable=False)

    quantity_sold = db.Column(db.Integer, default=0, nullable=False)
    date_sold = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())

    product = db.relationship('Product', backref=db.backref('sold_records', lazy=True))

    def __repr__(self):
        return f"<SoldItem {self.product_name} - {self.quantity_sold} on {self.date_sold}>"

# Category Model
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Category {self.name}>"

# Request Model (Customer Requests for Non-Listed Items)
class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Fulfilled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('User', backref=db.backref('requests', lazy=True))

    def __repr__(self):
        return f"<Request {self.product_name} by {self.customer_id}>"

# Order Model
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Paid, Delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.id} by {self.customer_id}>"

# OrderItem Model (Items in an Order)
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))

    def __repr__(self):
        return f"<OrderItem {self.product_id} in Order {self.order_id}>"

# Stock Log Model (For Tracking Stock Changes)
class StockLog(db.Model):
    __tablename__ = 'stock_logs'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)  # Positive for addition, negative for removal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('stock_logs', lazy=True))

    def __repr__(self):
        return f"<StockLog {self.quantity_change} for Product {self.product_id}>"

# Cart Model (For Shopping Cart)
class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    customer = db.relationship('User', backref=db.backref('cart', uselist=False))

    def __repr__(self):
        return f"<Cart for Customer {self.customer_id}>"

# CartItem Model (Items in the Cart)
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    cart = db.relationship('Cart', backref=db.backref('items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

    def __repr__(self):
        return f"<CartItem {self.product_id} in Cart {self.cart_id}>"

# Feedback Model (Customer Feedback)
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)  # Can be general feedback or product-specific
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # Optional rating (1-5 stars)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('User', backref=db.backref('feedback', lazy=True))
    product = db.relationship('Product', backref=db.backref('feedback', lazy=True))

    def __repr__(self):
        return f"<Feedback by Customer {self.customer_id}>"
class RequestItem(db.Model):
    """
    Model to store customer requests for items not available in the store.
    """
    __tablename__ = 'request_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name of the requested item
    description = db.Column(db.Text, nullable=True)   # Description of the requested item
    status = db.Column(db.String(20), default="Pending")  # Status (Pending, Fulfilled, etc.)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # The user who requested the item
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of the request

    user = db.relationship('User', backref='request_items', lazy=True)

    def __repr__(self):
        return f"<RequestItem {self.name} - Status: {self.status}>"
# Audit Log (System Logs)
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)  # Action performed (e.g., "Added Product", "Deleted User")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin or user who performed the action
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def __repr__(self):
        return f"<AuditLog {self.action}>"
