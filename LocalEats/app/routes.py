from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.models import User, Restaurant, MenuItem, Order, Review, Payment, Promotion, SubscriptionPlan, DeliveryTracking, Notification
from app.forms import RegistrationForm, LoginForm, CustomerLocationForm, RestaurantForm, MenuItemForm, OrderStatusForm, ReviewForm, PaymentForm, PromotionForm, SubscriptionPlanForm, DeliveryTrackingForm
from app.utils.logger import log_event
from app.utils.jwt_handler import token_required
from app.utils.response_helper import success_response, error_response
from app.utils.validators import validate_email
from app.services.auth_service import register_user, login_user_service
from app.services.restaurant_service import create_restaurant_service, get_restaurant_service
from app.services.menu_service import add_menu_item_service
from app.services.order_service import update_order_status_service, track_order_service
from app.services.notification_service import create_notification

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user, error = register_user(form)
        if error:
            flash(error, 'danger')
        else:
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('main.login'))
    return render_template('registration.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user, error = login_user_service(form)
        if error:
            flash(error, 'danger')
        else:
            login_user(user)
            flash('Logged in successfully.', 'success')
            if user.role == 'restaurant_owner':
                return redirect(url_for('main.restaurant_dashboard'))
            return redirect(url_for('main.customer_dashboard'))
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.home'))

@bp.route('/restaurant_dashboard')
@login_required
def restaurant_dashboard():
    restaurants = Restaurant.query.filter_by(user_id=current_user.id).all()
    return render_template('restaurant_dashboard.html', restaurants=restaurants)

@bp.route('/customer_dashboard')
@login_required
def customer_dashboard():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('customer_dashboard.html', orders=orders)

@bp.route('/restaurant/create', methods=['GET', 'POST'])
@login_required
def create_restaurant():
    form = RestaurantForm()
    if form.validate_on_submit():
        restaurant, error = create_restaurant_service(form, current_user)
        if error:
            flash(error, 'danger')
        else:
            flash('Restaurant created successfully.', 'success')
            return redirect(url_for('main.restaurant_dashboard'))
    return render_template('create_restaurant.html', form=form)

@bp.route('/restaurant/<int:restaurant_id>')
def view_restaurant(restaurant_id):
    restaurant, error = get_restaurant_service(restaurant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('main.home'))
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()
    return render_template('menu_list.html', restaurant=restaurant, menu_items=menu_items)

@bp.route('/restaurant/<int:restaurant_id>/add_menu_item', methods=['GET', 'POST'])
@login_required
def add_menu_item(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.restaurant_dashboard'))
    form = MenuItemForm()
    if form.validate_on_submit():
        item, error = add_menu_item_service(form, restaurant)
        if error:
            flash(error, 'danger')
        else:
            flash('Menu item added successfully.', 'success')
            return redirect(url_for('main.view_restaurant', restaurant_id=restaurant.id))
    return render_template('add_menu_item.html', form=form, restaurant=restaurant)

@bp.route('/order/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    form = OrderStatusForm()
    if form.validate_on_submit():
        success, error = update_order_status_service(order_id, form.status.data)
        if error:
            flash(error, 'danger')
        else:
            flash('Order status updated.', 'success')
    return redirect(request.referrer or url_for('main.restaurant_dashboard'))

@bp.route('/order/<int:order_id>/details')
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id and current_user.role != 'restaurant_owner':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('order_details.html', order=order)

@bp.route('/track_order/<int:order_id>')
@login_required
def track_order(order_id):
    tracking_info, error = track_order_service(order_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('main.customer_dashboard'))
    return render_template('order_tracking.html', tracking_info=tracking_info)

@bp.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

@bp.route('/data_protection_policy')
def data_protection_policy():
    return render_template('data_protection_policy.html')

@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

log_event('Routes initialized successfully')
