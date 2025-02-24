from flask import (
    render_template, redirect, url_for, flash, request, session, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.models import StockLog

from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
# app/routes.py
from flask import current_app as app
import logging
from datetime import date
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
csrf = CSRFProtect()
from app import  db, mail
from app.models import (
    User, Product, Category, Order, SelectedItem, Invoice, OrderItem, Feedback, RequestItem, Cart, AuditLog, Request, CartItem
)
from app.forms import (
    LoginForm, RegistrationForm,RegisterForm, ManageProductForm, ProfileForm, AddProductForm, ProductForm, RequestItemForm, FeedbackForm, UpdateProfileForm, EditUserForm, CartForm, BulkUploadForm
)
from app.utils import (
    save_image, get_out_of_stock_products, low_stock_alert, calculate_cart_total, log_action
)
import os
import fitz  # PyMuPDF for PDF processing
import docx 
# ----------------------------------
# Public Routes (Customer-facing)
# ----------------------------------
from flask import Blueprint

main = Blueprint('main', __name__)
logging.basicConfig(level=logging.DEBUG)
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
UPLOAD_FOLDER = 'app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main.route('/')
def home():
    """Homepage with product listings categorized & searchable, and displaying customer feedback"""
    query = request.args.get('query', '')
    category_id = request.args.get('category', '')
    form = FeedbackForm()

    # Get all categories
    categories = Category.query.all()

    # Fetch products based on category and search query
    if category_id:
        products_query = Product.query.filter_by(category_id=category_id).filter(Product.quantity > 0)
    else:
        products_query = Product.query.filter(Product.quantity > 0)

    if query:
        products_query = products_query.filter(Product.name.ilike(f"%{query}%"))

    products = products_query.limit(10).all()

    # Prepare categorized products dictionary
    categorized_products = {}
    if category_id:
        category = Category.query.get(category_id)
        if products:
            categorized_products[category] = products
    else:
        for category in categories:
            category_products = Product.query.filter_by(category_id=category.id).filter(Product.quantity > 0).all()
            if category_products:
                categorized_products[category] = category_products

    # Fetch the latest or top-rated feedback to replace static testimonials
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(3).all()

    return render_template(
        'home.html',
        categories=categories,
        categorized_products=categorized_products,
        feedbacks=feedbacks, form=form
    )


   
@main.route('/admin/sold-items', methods=['GET'])
@login_required
def view_sold_items():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    # Get filter option from query string
    filter_option = request.args.get('filter', 'day')  # default to 'day'

    today = datetime.today().date()

    if filter_option == 'day':
        sold_items = SoldItem.query.filter(SoldItem.date_sold == today).all()

    elif filter_option == 'week':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        sold_items = SoldItem.query.filter(
            SoldItem.date_sold >= start_of_week,
            SoldItem.date_sold <= end_of_week
        ).all()

    elif filter_option == 'month':
        sold_items = SoldItem.query.filter(
            func.extract('year', SoldItem.date_sold) == today.year,
            func.extract('month', SoldItem.date_sold) == today.month
        ).all()

    elif filter_option == 'year':
        sold_items = SoldItem.query.filter(
            func.extract('year', SoldItem.date_sold) == today.year
        ).all()

    else:
        sold_items = SoldItem.query.all()

    return render_template('view_sold_items.html', sold_items=sold_items, filter_option=filter_option)
from sqlalchemy import func


from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
import random
import string


@main.route('/admin/print-receipt/<string:document_number>', methods=['GET'])
@login_required
def print_receipt(document_number):
    # Get the selected items associated with this invoice number
    selected_items = SelectedItem.query.filter_by(document_number=document_number).all()

    if not selected_items:
        flash('No items found for the given invoice number.', 'danger')
        return redirect(url_for('main.select_items'))

    # Generate a unique receipt number (e.g., XYZ160225)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    date_part = datetime.utcnow().strftime('%d%m%y')  # e.g., 160225
    receipt_number = f"{random_letters}{date_part}"

    total_amount = 0

    for item in selected_items:
        # Reduce stock from Product table
        product = Product.query.get(item.product_id)
        if product:
            if product.quantity >= item.quantity:
                product.quantity -= item.quantity
                # If quantity becomes 0, mark as unavailable
                if product.quantity == 0:
                    product.is_available = False

                # Record in StockLog
                stock_log = StockLog(
                    product_id=product.id,
                    quantity_change=-item.quantity,  # Stock reduced
                    created_at=datetime.utcnow()
                )
                db.session.add(stock_log)

                # Record in SoldItem
                sold_item = SoldItem(
                    product_id=product.id,
                    product_name=product.name,
                    product_description=product.description,
                    product_price=product.price,
                    product_image=product.image,
                    product_category_id=product.category_id,
                    quantity_sold=item.quantity,
                    date_sold=datetime.utcnow().date()
                )
                db.session.add(sold_item)

                # Calculate the total price for this order
                total_amount += item.quantity * product.price
            else:
                flash(f"Insufficient stock for {product.name}. Available: {product.quantity}", 'danger')
                return redirect(url_for('main.view_selected_items'))

        # Mark the selected items as paid and assign receipt number
        item.is_paid = True
        item.document_number = receipt_number

    db.session.commit()

    flash('Receipt generated successfully. Stock updated.', 'success')

    # Render the receipt template for printing
    return render_template('print_receipt.html', selected_items=selected_items, document_number=receipt_number, total_amount=total_amount, date=datetime.utcnow().date())

@main.route('/admin/stock-logs', methods=['GET'])
@login_required
def view_stock_logs():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    # Get the filter from the query string (default to 'daily')
    filter_type = request.args.get('filter', 'daily')

    # Get current date and time
    now = datetime.utcnow()

    # Determine the start date based on the filter
    if filter_type == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == 'weekly':
        start_date = now - timedelta(days=now.weekday())  # Start of the week (Monday)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == 'yearly':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        # Invalid filter type, fallback to daily
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Fetch stock logs from the database based on the start date
    stock_logs = (
        db.session.query(StockLog)
        .join(Product)
        .filter(StockLog.created_at >= start_date)
        .order_by(StockLog.created_at.desc())
        .all()
    )

    return render_template('view_stock_logs.html', stock_logs=stock_logs, filter_type=filter_type)
@main.route('/admin/products-attention', methods=['GET'])
@login_required
def products_attention():
    """View for products that need attention (low stock) and requested items."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    # Products with stock less than or equal to 5
    low_stock_products = Product.query.filter(Product.quantity <= 5).all()

    # Requested items (Pending or all)
    requested_items = RequestItem.query.order_by(RequestItem.created_at.desc()).all()

    return render_template(
        'products_attention.html',
        low_stock_products=low_stock_products,
        requested_items=requested_items
    )

@main.route('/orders')
@login_required
def view_orders():
    if current_user.is_admin:
        # Admin sees all orders
        orders = Order.query.order_by(Order.created_at.desc()).all()
    elif current_user.is_seller:
            orders = Order.query.order_by(Order.created_at.desc()).all()  # Seller dashboard    
    else:
        # Regular user sees only their own orders
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()

    return render_template('orders.html', orders=orders)
    


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.location = form.location.data
        current_user.occupation = form.occupation.data

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('main.profile'))

    return render_template('profile.html', form=form)

   
@main.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page."""
    product = Product.query.get_or_404(product_id)
    form = CartForm()
    return render_template('product_detail.html', product=product, form=form)

from flask import render_template, Response
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from .models import Product, RequestItem
from . import db
from flask_login import login_required, current_user
import os

@main.route('/admin/print-items-needed', methods=['GET'])
@login_required
def print_items_needed():
    """Generate a PDF report of items needed (requested, out of stock, low stock)."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))  # Restrict access to admin only

    # Fetch requested items
    requested_items = RequestItem.query.all()

    # Fetch out-of-stock items
    out_of_stock_items = Product.query.filter_by(quantity=0).all()

    # Fetch low-stock items (quantity < 10)
    low_stock_items = Product.query.filter(Product.quantity < 10, Product.quantity > 0).all()

    # Create a PDF in memory
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Items Needed Report")

    # PDF Header
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(200, 750, "Items Needed Report")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(200, 735, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.line(50, 730, 550, 730)

    y = 710  # Start position for the content

    def draw_table_header(y_pos, title):
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_pos, title)
        pdf.setFont("Helvetica", 10)
        # Header Row
        pdf.drawString(50, y_pos - 15, "No.")
        pdf.drawString(100, y_pos - 15, "Name")
        pdf.drawString(300, y_pos - 15, "Description/Details")
        pdf.drawString(400, y_pos - 15, "Category")
        pdf.drawString(500, y_pos - 15, "Stock/Price")
        # Draw table header box
        pdf.rect(45, y_pos - 25, 510, 20)  # Full header row box
        return y_pos - 30  # Adjusted Y position after the header

    def draw_row(y_pos, idx, name, description, category, stock_price, row_height):
        # Ensure content fits within cells and text doesn't overflow
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y_pos, str(idx))  # Item number
        pdf.drawString(100, y_pos, name)
        pdf.drawString(300, y_pos, description)
        pdf.drawString(400, y_pos, category)
        pdf.drawString(500, y_pos, stock_price)
        
        # Draw row box
        pdf.rect(45, y_pos - 10, 510, row_height)  # Row box (slightly smaller than the header box)
        return y_pos - row_height  # Adjust Y position after the row

    # Add Requested Items
    if requested_items:
        y = draw_table_header(y, "Requested Items (Not in System):")
        for idx, item in enumerate(requested_items, 1):
            requester_name = item.user.username if item.user else "Unknown"
            y = draw_row(y, idx, item.name, item.description or "No Description", "N/A", "N/A", 20)

    # Add Out of Stock Items
    if out_of_stock_items:
        y -= 20
        y = draw_table_header(y, "Out of Stock Items:")
        for idx, item in enumerate(out_of_stock_items, 1):
            row_height = 20  # Default row height
            # If description or other content is large, increase row height
            description = item.description or "No Description"
            if len(description) > 50:  # Arbitrary length check for larger content
                row_height = 30
            y = draw_row(y, idx, item.name, description, item.category.name if item.category else "No Category", f"{item.price} / Stock: {item.quantity}", row_height)
            # Add product image if available
            if item.image:
                image_path = os.path.join('static', 'images', item.image)
                if os.path.exists(image_path):
                    pdf.drawImage(image_path, 60, y - 50, width=50, height=50)
                    y -= 60  # Adjust Y after the image
                else:
                    pdf.drawString(60, y, "Image not available.")
                    y -= 15

    # Add Low Stock Items
    if low_stock_items:
        y -= 20
        y = draw_table_header(y, "Low Stock Items (Below 10):")
        for idx, item in enumerate(low_stock_items, 1):
            row_height = 20  # Default row height
            description = item.description or "No Description"
            if len(description) > 50:  # Arbitrary length check for larger content
                row_height = 30
            y = draw_row(y, idx, item.name, description, item.category.name if item.category else "No Category", f"{item.price} / Stock: {item.quantity}", row_height)
            # Add product image if available
            if item.image:
                image_path = os.path.join('static', 'images', item.image)
                if os.path.exists(image_path):
                    pdf.drawImage(image_path, 60, y - 50, width=50, height=50)
                    y -= 60  # Adjust Y after the image
                else:
                    pdf.drawString(60, y, "Image not available.")
                    y -= 15

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return Response(buffer, mimetype='application/pdf', headers={"Content-Disposition": "attachment;filename=items_needed_report.pdf"})




@main.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add a product to the customer's cart."""
    form = CartForm()
    if not form.validate_on_submit():
        flash("Invalid form submission. Please try again.", "danger")
        return redirect(url_for('main.product_detail', product_id=product_id))

    # Fetch the product
    product = Product.query.get_or_404(product_id)

    # Validate quantity
    quantity = request.form.get('quantity', 1, type=int)
    if quantity < 1:
        flash("Quantity must be at least 1.", "danger")
        return redirect(url_for('main.product_detail', product_id=product_id))

    if product.quantity < quantity:
        flash(f"Only {product.quantity} units of {product.name} are available.", "danger")
        return redirect(url_for('main.product_detail', product_id=product_id))

    # Check if the user already has a cart
    user_cart = Cart.query.filter_by(customer_id=current_user.id).first()

    # Create a new cart if the user doesn't have one
    if not user_cart:
        user_cart = Cart(customer_id=current_user.id)
        db.session.add(user_cart)
        db.session.commit()

    # Check if the product is already in the user's cart
    existing_cart_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=product_id).first()

    if existing_cart_item:
        # Update the quantity of the existing item
        existing_cart_item.quantity += quantity
    else:
        # Add the product as a new item in the cart
        new_cart_item = CartItem(cart_id=user_cart.id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)

    # Deduct the stock from the product
    product.quantity -= quantity

    db.session.commit()

    flash(f"{product.name} has been added to your cart!", "success")
    return redirect(url_for('main.product_detail', product_id=product_id))


@main.route('/request-item', methods=['GET', 'POST'])
@login_required
def request_item():
    """Allow customers to request unavailable items."""
    form = RequestItemForm()
    if form.validate_on_submit():
        request_item = RequestItem(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(request_item)
        db.session.commit()
        flash("Your request has been submitted!", "success")
        return redirect(url_for('main.home'))
    return render_template('request_item.html', form=form)

@main.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    """View and manage the shopping cart."""
    
    # Get the user's cart
    user_cart = Cart.query.filter_by(customer_id=current_user.id).first()

    # If the user has no cart, initialize an empty list
    cart_items = user_cart.items if user_cart else []

    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)
@main.route('/update-cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    """Update item quantity in the cart."""
    quantity = request.form.get('quantity', type=int)

    user_cart = Cart.query.filter_by(customer_id=current_user.id).first()
    if not user_cart:
        flash("Cart not found!", "danger")
        return redirect(url_for('main.cart'))

    cart_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity = quantity
        db.session.commit()
        flash("Cart updated successfully!", "success")

    return redirect(url_for('main.cart'))


@main.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    """Remove an item from the cart."""
    user_cart = Cart.query.filter_by(customer_id=current_user.id).first()
    if not user_cart:
        flash("Cart not found!", "danger")
        return redirect(url_for('main.cart'))

    cart_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Item removed from cart!", "info")

    return redirect(url_for('main.cart'))

from .forms import CheckoutForm
@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Display the checkout page (GET) and handle order processing (POST)."""

    # Fetch the cart for the current user
    cart = Cart.query.filter_by(customer_id=current_user.id).first()
    form = CheckoutForm()  # Initialize the form

    if request.method == "GET":
        if not cart or not cart.items:
            flash("Your cart is empty! Add items before checking out.", "warning")
            return redirect(url_for('main.cart'))

        # Compute total amount and attach total_price dynamically
        cart_items = []
        total_amount = 0

        for item in cart.items:
            total_price = item.product.price * item.quantity
            total_amount += total_price

            # Manually create a dictionary with total_price
            item_data = {
                'product': item.product,
                'quantity': item.quantity,
                'total_price': total_price  # Attach total_price dynamically
            }
            cart_items.append(item_data)

        return render_template("checkout.html", cart_items=cart_items, total_amount=total_amount, form=form)

    # Handle checkout process on POST request
    if form.validate_on_submit():  # Validate CSRF token
        if not cart or not cart.items:
            flash("Your cart is empty! Add items before checking out.", "warning")
            return redirect(url_for('main.cart'))

        # Compute total amount for the order
        total_order_price = sum(item.product.price * item.quantity for item in cart.items)

        # Create a new order with the total price
        order = Order(
            customer_id=current_user.id,
            total_price=total_order_price,  # Ensure this field is set
            status="Pending"
        )
        db.session.add(order)
        db.session.flush()  # Get order ID before committing

        for item in cart.items:
            if item.product.quantity < item.quantity:
                flash(f"Not enough stock for {item.product.name}. Reduce quantity or choose another product.", "danger")
                return redirect(url_for('main.cart'))

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
            item.product.quantity -= item.quantity  # Reduce stock

        # Clear the cart after order placement
        CartItem.query.filter_by(cart_id=cart.id).delete()

        db.session.commit()

        flash("Your order has been placed successfully!", "success")
        return redirect(url_for('main.home'))

    flash("Invalid form submission. Please try again.", "danger")
    return redirect(url_for('main.checkout'))




@main.route('/feedback/<int:product_id>', methods=['GET', 'POST'])
@login_required
def feedback(product_id):
    """Allow customers to submit feedback on a product."""
    product = Product.query.get_or_404(product_id)
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            product_id=product.id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(feedback)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
        return redirect(url_for('product_detail', product_id=product.id))
    return render_template('feedback.html', form=form, product=product)

# ----------------------------------
# Authentication Routes
# ----------------------------------


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration."""
    
    # Check if the user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            # Check if the username already exists
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash("Username already taken. Please choose another one.", "danger")
                logging.warning(f"Attempt to register with an already existing username: {form.username.data}")
                return redirect(url_for('main.register'))

            # Hash the password
            hashed_password = generate_password_hash(form.password.data)

            # Create a new User object, including location details
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                county=form.county.data,
                subcounty=form.subcounty.data,
                street=form.street.data
            )

            # Add the user to the database and commit the transaction
            db.session.add(user)
            db.session.commit()

            # Log the successful registration
            logging.info(f"User {form.username.data} registered successfully.")
            
            # Show success message and redirect to login page
            flash("Your account has been created! Please log in.", "success")
            return redirect(url_for('main.login'))

        except Exception as e:
            # Log the exception if an error occurs
            logging.error(f"Error during registration: {e}")
            flash("An error occurred while creating your account. Please try again.", "danger")
            return redirect(url_for('main.register'))
    
    # Render the registration form if not submitted or invalid
    if form.errors:
        logging.error(f"Form validation failed with errors: {form.errors}")
    
    return render_template('register.html', form=form)
from app.forms import RequestResetForm, ResetPasswordForm
from flask_mail import Message
@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        # Redirect authenticated users based on their role
        if current_user.is_admin:
            return redirect(url_for('main.admin_dashboard'))  # Shop owner/admin dashboard
        elif current_user.is_seller:
            return redirect(url_for('main.seller_dashboard'))  # Seller dashboard
        else:
            return redirect(url_for('main.home'))  # Customer home

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # Log the user in
            login_user(user, remember=form.remember.data)
            
            # Redirect based on the user role
            if user.is_admin:
                return redirect(url_for('main.admin_dashboard'))  # Admin Dashboard
            elif user.is_seller:
                return redirect(url_for('main.seller_dashboard'))  # Seller Dashboard
            else:
                return redirect(url_for('main.home'))  # Customer Home

        flash("Login failed. Check email and password.", "danger")
    
    return render_template('login.html', form=form)

@main.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    """Handles the request to reset password."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash("If an account with that email exists, a reset link has been sent.", "info")
        return redirect(url_for('main.login'))

    return render_template('reset_request.html', form=form)

def send_reset_email(user):
    """Send a password reset email with a token link."""
    token = user.get_reset_token()
    reset_url = url_for('main.reset_token', token=token, _external=True)
    msg = Message('Password Reset Request', sender='noreply@example.com', recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{reset_url}

If you did not request this, please ignore this email.
"""
    mail.send(msg)

@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """Handles the password reset via token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash("Invalid or expired token.", "warning")
        return redirect(url_for('main.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated! You can now log in.", "success")
        return redirect(url_for('main.login'))

    return render_template('reset_token.html', form=form)


@main.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.home'))

# ----------------------------------
# Admin Routes
# ----------------------------------

@main.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Route to edit user details."""
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash("User details updated successfully!", "success")
        return redirect(url_for('main.manage_users'))

    return render_template('edit_user.html', form=form, user=user)
@main.route('/admin/delete-user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    """Route to delete a user."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User has been deleted.", "danger")
    return redirect(url_for('main.manage_users'))

from sqlalchemy.orm import aliased
from sqlalchemy import func

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    # Total products and total orders
    total_products = Product.query.count()
    total_orders = Order.query.count()
    
    # Out of stock products: those with quantity 0 and is_available = False
    out_of_stock_count = Product.query.filter(Product.quantity == 0, Product.is_available == False).count()

    # New requests (assuming RequestItem has a status field)
    new_requests = RequestItem.query.count()

    # Get recent activities if any (this is just a placeholder, update according to your model)
    recent_activities = [
        {"message": "Product Stock Updated", "timestamp": "2025-02-04 12:34:56"},
        {"message": "Order Received", "timestamp": "2025-02-03 08:30:21"},
    ]
    
    return render_template(
        'admin_dashboard.html',
        total_products=total_products,
        total_orders=total_orders,
        out_of_stock_count=out_of_stock_count,
        new_requests=new_requests,
        recent_activities=recent_activities
    )
from app.models import Product, SoldItem
@main.route('/admin/manage-products', methods=['GET', 'POST'])
@login_required
def manage_products():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    form = ManageProductForm()

    # Populate dropdown with products
    form.product_id.choices = [(p.id, p.name) for p in Product.query.all()]

    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)

        if product:
            today = date.today()
            quantity_sold = form.quantity_sold.data
            quantity_added = form.quantity_added.data

            # Process selling of product (reduce stock and record sold item)
            if quantity_sold > 0:
                if quantity_sold > product.quantity:
                    flash(f"Insufficient stock for {product.name}.", 'danger')
                else:
                    # Reduce stock
                    product.quantity -= quantity_sold

                    # Log stock reduction
                    stock_log = StockLog(product_id=product.id, quantity_change=-quantity_sold)
                    db.session.add(stock_log)

                    # Record sold item in SoldItem table (check if same product sold today)
                    sold_item = SoldItem.query.filter_by(product_id=product.id, date_sold=today).first()

                    if sold_item:
                        sold_item.quantity_sold += quantity_sold
                    else:
                        sold_item = SoldItem(
                            product_id=product.id,
                            product_name=product.name,
                            product_description=product.description,
                            product_price=product.price,
                            product_image=product.image,
                            product_category_id=product.category_id,
                            quantity_sold=quantity_sold,
                            date_sold=today
                        )
                        db.session.add(sold_item)

                    flash(f'{quantity_sold} {product.name}(s) marked as sold.', 'success')

            # Process adding stock
            if quantity_added > 0:
                product.quantity += quantity_added

                # Log stock addition
                stock_log = StockLog(product_id=product.id, quantity_change=quantity_added)
                db.session.add(stock_log)

                flash(f'{quantity_added} {product.name}(s) added to stock.', 'success')

            # Update product availability status
            product.is_available = product.quantity > 0

            db.session.commit()
            return redirect(url_for('main.manage_products'))
        else:
            flash("Product not found!", 'danger')

    return render_template('manage_products.html', form=form)


import os
import logging
import docx
import fitz  # PyMuPDF
from datetime import datetime


# Ensure logs directory exists
LOG_FOLDER = 'app/logs'
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, 'upload_log.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(base_filename):
    """Generate a unique filename to avoid overwriting existing files."""
    filename, ext = os.path.splitext(base_filename)
    counter = 1
    unique_filename = base_filename

    while os.path.exists(os.path.join(UPLOAD_FOLDER, unique_filename)):
        unique_filename = f"{filename}_{counter}{ext}"
        counter += 1

    return unique_filename


def save_image(image_data, product_name):
    """Save the extracted image using the product name as the filename."""
    if not image_data:
        return None  # If there's no image data, return None

    sanitized_name = secure_filename(product_name.replace(" ", "_").lower())
    image_filename = f"{sanitized_name}.jpg"
    image_filename = generate_unique_filename(image_filename)
    image_path = os.path.join(UPLOAD_FOLDER, image_filename)

    try:
        with open(image_path, "wb") as img_file:
            img_file.write(image_data)  # Ensure image_data is in bytes
        logging.info(f"Image saved: {image_filename}")
        return image_filename
    except Exception as e:
        logging.error(f"Error saving image {image_filename}: {e}")
        return None


@main.route('/admin/upload-bulk-products', methods=['POST'])
@login_required
def upload_bulk_products():
    """Handle bulk product uploads from a Word (.docx) or PDF (.pdf) file."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    file = request.files.get('file')

    if not file or not allowed_file(file.filename):
        flash("Invalid file type. Please upload a .docx or .pdf file.", "danger")
        logging.warning("Invalid file type attempted for upload.")
        return redirect(url_for('main.add_product'))

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    logging.info(f"File uploaded: {filename}")

    try:
        if filename.endswith('.pdf'):
            products = extract_products_from_pdf(file_path)
        elif filename.endswith('.docx'):
            products = extract_products_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format.")

        if not products:
            flash("No products found in the file.", "danger")
            logging.warning("No products extracted from the uploaded file.")
            return redirect(url_for('main.admin_dashboard'))

        added_products_count = 0

        for product_data in products:
            category_name = product_data['category'].strip()
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()
                logging.info(f"New category added: {category_name}")

            image_filename = None
            if product_data['image']:
                image_filename = save_image(product_data['image'], product_data['name'])

            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                quantity=product_data['quantity'],
                category_id=category.id,
                image=image_filename,
                created_at=datetime.utcnow(),
                is_available=product_data['quantity'] > 0
            )

            db.session.add(product)
            db.session.commit()  # Commit product to get ID

            # Log initial stock addition in StockLog
            if product.quantity > 0:
                stock_log = StockLog(
                    product_id=product.id,
                    quantity_change=product.quantity,
                    created_at=datetime.utcnow()
                )
                db.session.add(stock_log)
                db.session.commit()
                logging.info(f"Stock log added for product '{product.name}' with initial quantity {product.quantity}")

            added_products_count += 1
            logging.info(f"Product '{product.name}' added with image '{image_filename}'")

        flash(f"Successfully added {added_products_count} products from the file.", "success")
        logging.info(f"Bulk upload successful: {added_products_count} products added.")

    except Exception as e:
        flash(f"Error processing file: {str(e)}", "danger")
        logging.error(f"Error processing file {filename}: {str(e)}")

    finally:
        os.remove(file_path)
        logging.info(f"Uploaded file removed: {filename}")

    return redirect(url_for('main.admin_dashboard'))


def extract_products_from_docx(file_path):
    """Extract product data and images from a Word (.docx) file."""
    doc = docx.Document(file_path)
    products = []
    image_map = {}

    for rel_id, rel in doc.part.rels.items():
        if "image" in rel.target_ref:
            try:
                image_data = rel.target_part.blob
                image_map[rel_id] = image_data  # Store image as bytes
                logging.info(f"Extracted image (rel_id: {rel_id})")
            except Exception as e:
                logging.error(f"Error extracting image: {e}")

    first_row = True

    for table in doc.tables:
        for row in table.rows:
            cells = row.cells

            if first_row:
                first_row = False
                continue

            if len(cells) == 6:
                try:
                    product_name = cells[0].text.strip()
                    image_rel_id = cells[1]._element.xpath('.//a:blip/@r:embed')

                    price = cells[2].text.strip()
                    description = cells[3].text.strip()
                    category = cells[4].text.strip()
                    quantity = cells[5].text.strip()

                    image_data = None
                    if image_rel_id:
                        image_rel_id = image_rel_id[0]
                        image_data = image_map.get(image_rel_id)

                    products.append({
                        'name': product_name,
                        'image': image_data,
                        'price': float(price) if price.replace('.', '', 1).isdigit() else 0.0,
                        'description': description,
                        'category': category,
                        'quantity': int(quantity) if quantity.isdigit() else 0
                    })

                except Exception as e:
                    logging.error(f"Error processing product '{product_name}': {e}")

    return products


def extract_products_from_pdf(file_path):
    """Extract product data from a PDF file."""
    doc = fitz.open(file_path)
    products = []
    image_map = {}

    for page in doc:
        for img_index, img in enumerate(page.get_images(full=True), start=1):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                image_map[img_index] = image_data  # Store image as bytes
                logging.info(f"Extracted image for index {img_index}")
            except Exception as e:
                logging.error(f"Error extracting image at index {img_index}: {e}")

    for page in doc:
        text = page.get_text("text")
        lines = text.split("\n")

        for line in lines:
            parts = line.split(",")
            if len(parts) == 6:
                try:
                    image_index = int(parts[1].strip()) if parts[1].strip().isdigit() else None
                    image_data = image_map.get(image_index)

                    products.append({
                        'name': parts[0].strip(),
                        'image': image_data,
                        'price': float(parts[2].strip()),
                        'description': parts[3].strip(),
                        'category': parts[4].strip(),
                        'quantity': int(parts[5].strip())
                    })

                except Exception as e:
                    logging.error(f"Error processing product {parts[0].strip()}: {e}")

    return products





@main.route('/admin/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add a single product with category handling or upload products in bulk."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))  # Restrict access to admins

    form = AddProductForm()
    bulk_upload_form = BulkUploadForm()

    # Populate category dropdown with existing categories
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():  # When the single product form is submitted
        image_file = None
        if form.image.data:
            image_file = save_image(form.image.data.read(), form.name.data)

        category_id = form.category_id.data
        new_category_name = request.form.get('new_category')  # Check if a new category is entered

        if new_category_name:  # If a new category is provided
            category = Category.query.filter_by(name=new_category_name.strip()).first()
            if not category:
                category = Category(name=new_category_name.strip())
                db.session.add(category)
                db.session.commit()
            category_id = category.id  # Assign the new category ID

        # Create the product
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            image=image_file,
            category_id=category_id,
            created_at=datetime.utcnow(),
            is_available=form.quantity.data > 0  # Set availability based on stock
        )

        db.session.add(product)
        db.session.commit()

        # Log the initial stock addition to StockLog
        if product.quantity > 0:
            stock_log = StockLog(
                product_id=product.id,
                quantity_change=product.quantity,  # Initial stock added
                created_at=datetime.utcnow()
            )
            db.session.add(stock_log)
            db.session.commit()

        flash("Product has been added successfully!", "success")
        return redirect(url_for('main.admin_dashboard'))

    return render_template('add_product.html', form=form, bulk_upload_form=bulk_upload_form)
from flask import request, redirect, url_for, flash, render_template
from datetime import datetime
import random
import string
from sqlalchemy.exc import IntegrityError

def generate_document_number():
    date_part = datetime.now().strftime("%d%m%y")
    prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
    unique_part = ''.join(random.choices(string.digits, k=3))  # Extra uniqueness
    return f"{prefix}{date_part}{unique_part}"

@main.route('/admin/select-items', methods=['GET', 'POST'])
def select_items():
    products = Product.query.filter(Product.quantity > 0).all()
    form = CSRFForm()

    if request.method == 'POST' and form.validate_on_submit():
        product_ids = request.form.getlist('product_ids[]')
        quantities = request.form.getlist('quantities[]')

        document_number = generate_document_number()  # One number for all selected items

        try:
            for i, product_id in enumerate(product_ids):
                product = Product.query.get(product_id)
                quantity = int(quantities[i])

                if product and quantity > 0:
                    selected_item = SelectedItem(
                        product_name=product.name,
                        description=product.description,
                        price=product.price,
                        quantity=quantity,
                        document_number=document_number,  # Same document number for all
                        is_paid=False
                    )
                    db.session.add(selected_item)

            db.session.commit()

            flash(f"Items selected successfully. Document Number: {document_number}", "success")
            return redirect(url_for('main.view_selected_items', document_number=document_number))

        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", "danger")

    return render_template('select_items.html', products=products, form=form)



 
from flask import render_template, request, redirect, url_for, flash, Response
from weasyprint import HTML

import random
import string

@main.route('/admin/search-invoice', methods=['GET'])
def search_invoice():
    document_number = request.args.get('document_number')
    search_attempted = False

    if document_number:
        # If searching, filter by document number (partial match)
        results = Invoice.query.filter(
            Invoice.document_number.ilike(f"%{document_number}%")
        ).all()
        search_attempted = True
    else:
        # Default: Show all invoices
        results = Invoice.query.order_by(Invoice.printed_at.desc()).all()

    return render_template(
        'search_invoice.html',
        results=results,
        search_attempted=search_attempted,
        document_number=document_number
    )

@main.route('/submit-feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Handle customer feedback submission"""
    comment = request.form.get('comment')
    rating = request.form.get('rating')

    # Convert rating to integer if provided
    rating = int(rating) if rating else None

    feedback = Feedback(
        customer_id=current_user.id,
        comment=comment,
        rating=rating,
    )

    db.session.add(feedback)
    db.session.commit()
    flash('Thank you for your feedback!', 'success')

    return redirect(url_for('main.home'))

from flask import render_template_string
from datetime import datetime


from datetime import datetime

@main.route('/admin/view-selected-items/<document_number>', methods=['GET', 'POST'])
def view_selected_items(document_number):
    selected_items = SelectedItem.query.filter_by(document_number=document_number).all()
    form = CartForm()

    if not selected_items:
        flash('Document not found.', 'danger')
        return redirect(url_for('main.select_items'))

    if request.method == 'POST':
        for item in selected_items:
            if not item.is_paid:
                product = Product.query.filter_by(name=item.product_name).first()

                if product:
                    # Update stock in Product table
                    product.quantity -= item.quantity
                    if product.quantity < 0:
                        product.quantity = 0

                    # Log stock change
                    stock_log = StockLog(
                        product_id=product.id,
                        quantity_change=-item.quantity
                    )
                    db.session.add(stock_log)

                    # Create SoldItem record
                    sold_item = SoldItem(
                        product_id=product.id,
                        product_name=product.name,
                        product_description=product.description,
                        product_price=product.price,
                        product_image=product.image,  # Assuming your Product model has image_url
                        product_category_id=product.category_id,
                        quantity_sold=item.quantity,
                        date_sold=datetime.utcnow().date()
                    )
                    db.session.add(sold_item)

                # Mark the SelectedItem as paid
                item.is_paid = True

        db.session.commit()
        flash(f"Document {document_number} marked as paid. Stock updated and sales recorded.", "success")
        return redirect(url_for('main.view_selected_items', document_number=document_number))

    grand_total = sum(item.price * item.quantity for item in selected_items)
    all_paid = all(item.is_paid for item in selected_items)

    if request.args.get('save_invoice') == '1':
        existing_invoice = Invoice.query.filter_by(document_number=document_number).first()

        if not existing_invoice:
            html_content = render_template(
                'print_invoice_template.html',
                selected_items=selected_items,
                document_number=document_number,
                grand_total=grand_total,
                all_paid=all_paid,
                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )

            invoice = Invoice(
                document_number=document_number,
                content=html_content,
                grand_total=grand_total,
                is_paid=all_paid,
                created_at=datetime.utcnow()
            )
            db.session.add(invoice)
            db.session.commit()

            flash(f"{'Receipt' if all_paid else 'Invoice'} saved successfully for Document {document_number}.", "info")
        else:
            flash(f"{'Receipt' if all_paid else 'Invoice'} for Document {document_number} already exists.", "warning")

        return redirect(url_for('main.view_selected_items', document_number=document_number))

    return render_template(
        'view_selected_items.html',
        selected_items=selected_items,
        document_number=document_number,
        form=form,
        grand_total=grand_total,
        all_paid=all_paid
    )






@main.route('/admin/print-document/<document_number>', methods=['GET'])
def print_document(document_number):
    """Generate and print PDF invoice or receipt"""
    selected_items = SelectedItem.query.filter_by(document_number=document_number).all()

    if not selected_items:
        flash("No items found for this document number.", "danger")
        return redirect(url_for('main.view_selected_items'))

    is_receipt = selected_items[0].is_paid  # Use this to differentiate invoice vs receipt

    total_amount = sum(item.price * item.quantity for item in selected_items)

    html = render_template(
        'print_pdf_document.html',
        document_number=document_number,
        items=selected_items,
        total_amount=total_amount,
        is_receipt=is_receipt,
        date=datetime.now().strftime("%d/%m/%Y"),
    )

    pdf_file = HTML(string=html).write_pdf()

    response = Response(pdf_file, content_type='application/pdf')
    response.headers['Content-Disposition'] = f'inline; filename={document_number}.pdf'
    return response

from datetime import datetime
import random
import string

def generate_invoice_number():
    date_str = datetime.now().strftime('%d%m%y')  # Example: 160225
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"{random_letters}{date_str}"

def generate_receipt_number():
    date_str = datetime.now().strftime('%d%m%y')  # Example: 160225
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"{random_letters}{date_str}"





@main.route('/admin/manage-requests')
@login_required
def manage_requests():
    """Manage item requests from customers."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    form = CSRFForm()
    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of requests to display per page
    
    # Fixing the query with proper pagination call
    requests = RequestItem.query.join(User).filter(RequestItem.user_id == User.id).order_by(RequestItem.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('manage_requests.html', requests=requests, form =form)
@main.route('/admin/create-seller', methods=['GET', 'POST'])
@login_required
def create_seller():
    """Admin creates a new seller."""
    if current_user.role != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.home'))

    form = RegisterForm()  # Use an existing form or create a new one for sellers
    if form.validate_on_submit():
        new_seller = User(
            username=form.username.data,
            email=form.email.data,
            role="seller"  # Assign the seller role
        )
        new_seller.set_password(form.password.data)
        db.session.add(new_seller)
        db.session.commit()
        flash("Seller account created successfully.", "success")
        return redirect(url_for('main.manage_sellers'))

    return render_template('create_seller.html', form=form)
@main.route('/manage_sellers', methods=['GET', 'POST'])
@login_required
def manage_sellers():
    """Admin view to manage sellers (add/delete)."""
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('main.index'))
    form = CartForm()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email or username exists
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash("User with this email or username already exists.", "warning")
            return redirect(url_for('main.manage_sellers'))

        # Create seller
        hashed_password = generate_password_hash(password)
        new_seller = User(username=username, email=email, password=hashed_password, role='seller')
        db.session.add(new_seller)
        db.session.commit()
        
        flash(f"Seller {username} added successfully.", "success")
        return redirect(url_for('main.manage_sellers'))

    # Fetch all sellers
    sellers = User.query.filter_by(role="seller").all()
    
    return render_template('manage_sellers.html', sellers=sellers, form = form)


@main.route('/delete_seller/<int:seller_id>', methods=['POST'])
@login_required
def delete_seller(seller_id):
    """Route to delete a seller."""
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('main.index'))

    seller = User.query.get_or_404(seller_id)
    db.session.delete(seller)
    db.session.commit()
    
    flash("Seller deleted successfully.", "success")
    return redirect(url_for('main.manage_sellers'))
@main.route('/seller/dashboard')
@login_required
def seller_dashboard():
    """Seller Dashboard - Manage products and orders"""
    if not current_user.is_seller:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.home'))

    # Fetch products managed by the seller
    products = Product.query.all()
    
    # Fetch orders for the seller's products
    orders = Order.query.join(OrderItem).all()

    return render_template('seller_dashboard.html', products=products, orders=orders)

@main.route('/admin/view-request/<int:request_id>')
@login_required
def view_request(request_id):
    """View the details of a specific request."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    # Fetch the request item by its ID
    request_item = RequestItem.query.get_or_404(request_id)
    
    return render_template('view_request.html', request=request_item)
@main.route('/admin/delete-request/<int:request_id>', methods=['POST'])
@login_required
def delete_request(request_id):
    """Admin route to delete a customer request."""
    
    # Ensure only admins can access this route
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.home'))

    request_item = RequestItem.query.get_or_404(request_id)
    form = CSRFForm()  # CSRF Protection

    if form.validate_on_submit():
        try:
            db.session.delete(request_item)  # Delete the request item
            db.session.commit()  # Commit changes
            flash(f"Request '{request_item.name}' has been deleted successfully.", "success")
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash("An error occurred while deleting the request. Please try again.", "danger")
    else:
        flash("Invalid request. Please try again.", "danger")

    return redirect(url_for('main.manage_requests'))  # Redirect back to request management



from app.forms import CSRFForm

# Optionally exempt CSRF protection for a specific route
@main.route('/admin/manage-stock', methods=['GET', 'POST'])
@login_required
def manage_stock():
    """Admin view to manage stock levels."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    products = Product.query.all()  # Get all products
    form = CSRFForm()  # Ensure we use CSRF token validation

    if request.method == 'POST' and form.validate_on_submit():
        product_id = request.form.get('product_id')
        action = request.form.get('action')
        quantity = request.form.get('quantity', type=int, default=0)

        product = Product.query.get_or_404(product_id)

        if action == 'increase':
            if quantity > 0:
                product.quantity += quantity

                # Log stock addition
                stock_log = StockLog(product_id=product.id, quantity_change=quantity)
                db.session.add(stock_log)

                db.session.commit()
                flash(f"Stock for {product.name} increased by {quantity} units.", "success")
            else:
                flash("Invalid quantity. Quantity must be greater than zero.", "danger")

        elif action == 'decrease':
            if quantity > 0 and product.quantity >= quantity:
                # Reduce stock
                product.quantity -= quantity

                # Record stock reduction in StockLog
                stock_log = StockLog(product_id=product.id, quantity_change=-quantity)
                db.session.add(stock_log)

                # Record sold item in SoldItem table
                today = date.today()
                sold_item = SoldItem.query.filter_by(product_id=product.id, date_sold=today).first()

                if sold_item:
                    sold_item.quantity_sold += quantity
                else:
                    sold_item = SoldItem(
                        product_id=product.id,
                        product_name=product.name,
                        product_description=product.description,
                        product_price=product.price,
                        product_image=product.image,
                        product_category_id=product.category_id,
                        quantity_sold=quantity,
                        date_sold=today
                    )
                    db.session.add(sold_item)

                # Update availability status
                product.is_available = product.quantity > 0

                db.session.commit()
                flash(f"Stock for {product.name} decreased by {quantity} units and recorded as sold.", "success")
            else:
                flash(f"Invalid operation. Check stock levels for {product.name}.", "danger")

        elif action == 'delete':
            if product.quantity > 0:
                # Log stock reduction for remaining quantity
                stock_log = StockLog(product_id=product.id, quantity_change=-product.quantity)
                db.session.add(stock_log)

            # Set stock to zero and mark as unavailable
            product.quantity = 0
            product.is_available = False

            db.session.commit()
            flash(f"{product.name} has been marked as unavailable.", "warning")

        return redirect(url_for('main.manage_stock'))

    return render_template('manage_stock.html', products=products, form=form)





@main.route('/admin/manage-orders', methods=['GET', 'POST'])
@login_required
def manage_orders():
    """Admin view to manage customer orders."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    orders = Order.query.all()  # Get all orders

    # Handle order status update
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        action = request.form.get('action')
        order = Order.query.get_or_404(order_id)

        if action == 'update_status':
            new_status = request.form.get('status')
            order.status = new_status
            db.session.commit()
            flash(f"Order status for Order ID {order.id} has been updated to {new_status}.", "success")
        
        return redirect(url_for('main.manage_orders'))

    return render_template('manage_orders.html', orders=orders)
# ----------------------------------
# Error Handlers
# ----------------------------------

@main.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Admin route to edit an existing product."""
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()  # Fetch all categories

    # Initialize the form and pre-fill with product data
    form = ProductForm(obj=product)

    # Ensure category choices are populated before validation
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():  # This checks for CSRF token and validation
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.category_id = form.category_id.data
        product.is_available = form.is_available.data

        # Handle image upload
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)  # Save directly in uploads folder

            image_file.save(image_path)
            product.image = f"{filename}"  # Store relative path

        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for('main.admin_dashboard'))  # Redirect to admin panel

    return render_template("edit_product.html", product=product, categories=categories, form=form)


@main.route('/admin/delete-product/<int:product_id>', methods=['GET'])
@login_required
def delete_product(product_id):
    """Route to mark a product as unavailable instead of deleting it."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    product = Product.query.get_or_404(product_id)

    # Set stock to 0 and mark as unavailable instead of deleting
    product.quantity = 0
    product.is_available = False

    db.session.commit()
    flash("Product has been marked as unavailable.", "warning")
    return redirect(url_for('main.manage_products'))

@main.route('/about')
def about():
    """Render the About Us page."""
    return render_template('about.html')

from app.forms import ContactForm    
@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Render the contact page and handle form submissions."""
    form = ContactForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        # You can process the form data here, e.g., send an email or store it in the database
        flash("Your message has been sent! We will get back to you soon.", "success")
        return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form)


@main.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404
@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()

    if query:
        # Perform a case-insensitive search for products matching the query
        # Searching by product name (or other fields like description, etc.)
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()

        # You can also include fuzzy matching if you prefer
        # For example, you can use `fuzzywuzzy` here to perform better matching (optional)
    else:
        products = []

    return render_template('search_results.html', products=products, query=query)
@main.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500
from app.models import Order

@main.route('/admin/orders')
@login_required
def amanage_orders():
    """Admin view to manage orders."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    # Fetch all orders, you can add filters here as needed
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)
@main.route('/admin/low_stock_alert_view')
@login_required
def low_stock_alert_view():
    """Admin view for low stock products."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    # Query for products with low stock (e.g., less than or equal to 5 units)
    low_stock_products = Product.query.filter(Product.quantity <= 5).all()

    return render_template('low_stock_alert_view.html', low_stock_products=low_stock_products)
@main.route('/admin/order/<int:order_id>')
@login_required
def view_order(order_id):
    """View details of a specific order."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    order = Order.query.get_or_404(order_id)
    return render_template('view_order.html', order=order)
from flask_wtf import FlaskForm
from wtforms import IntegerField
@main.route('/admin/order/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    """Delete an order."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    
    flash('Order has been deleted!', 'success')
    return redirect(url_for('main.manage_orders'))
class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', default=1)

@main.route('/shop', methods=['GET', 'POST'])
def shop():
    # Fetch all products available for sale
    products = Product.query.filter(Product.is_available == True).all()  # Assuming there's an 'is_available' flag

    # Create an instance of the form
    form = AddToCartForm()

    # If the form is submitted, you can handle the form data here (like adding to the cart)
    if form.validate_on_submit():
        # Handle adding the product to the cart (you can call the add_to_cart function here)
        pass

    # Pass the products and form to the template
    return render_template('shop.html', products=products, form=form)

    return render_template('shop.html', products=products)
@main.route('/admin/manage-users', methods=['GET', 'POST'])
@login_required
def manage_users():
    """Admin view to manage store users."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    users = User.query.all()  # Get all users

    # Handle user role updates and deletions
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        user = User.query.get_or_404(user_id)

        if action == 'update_role':
            new_role = request.form.get('role')
            user.role = new_role
            db.session.commit()
            flash(f"User role for {user.username} has been updated to {new_role}.", "success")
        
        if action == 'delete_user':
            db.session.delete(user)
            db.session.commit()
            flash(f"User {user.username} has been deleted.", "success")

        return redirect(url_for('main.manage_users'))

    return render_template('manage_users.html', users=users)

# routes.py (continued)

@main.route('/admin/user/<int:user_id>', methods=['GET'])
@login_required
def view_user(user_id):
    """Admin view to see the details of a specific user."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)
@main.route('/admin/products', methods=['GET'])
@login_required
def view_products():
    """View all products in the admin dashboard."""
    if not current_user.is_admin:
        return redirect(url_for('main.home'))  # Restrict access to admins
    
    products = Product.query.all()  # Fetch all products from the database
    return render_template('view_products.html', products=products)
