from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, SelectField, IntegerField, BooleanField, DecimalField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('restaurant_owner', 'Restaurant Owner')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CustomerLocationForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    live_location = StringField('Live Location (Optional)', validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(min=10, max=15)])
    submit = SubmitField('Save Location')


class RestaurantForm(FlaskForm):
    name = StringField('Restaurant Name', validators=[DataRequired()])
    location_coverage = StringField('Delivery Coverage Area', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(min=10, max=15)])
    description = TextAreaField('Description', validators=[Optional()])
    is_open = BooleanField('Open for Business')
    submit = SubmitField('Save Restaurant Details')


class MenuItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    availability = BooleanField('Available')
    image_url = StringField('Image URL', validators=[Optional()])
    submit = SubmitField('Add Item')


class OrderStatusForm(FlaskForm):
    status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Preparing', 'Preparing'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], validators=[DataRequired()])
    submit = SubmitField('Update Status')


class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional()])
    submit = SubmitField('Submit Review')


class PaymentForm(FlaskForm):
    payment_method = SelectField('Payment Method', choices=[('Mpesa', 'Mpesa'), ('PayPal', 'PayPal'), ('Cash', 'Cash')], validators=[DataRequired()])
    transaction_id = StringField('Transaction ID (Optional)', validators=[Optional()])
    submit = SubmitField('Confirm Payment')


class DeliveryTrackingForm(FlaskForm):
    status = SelectField('Delivery Status', choices=[('Preparing', 'Preparing'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered')], validators=[DataRequired()])
    location = StringField('Current Location (Optional)', validators=[Optional()])
    submit = SubmitField('Update Tracking')


class PromotionForm(FlaskForm):
    title = StringField('Promotion Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    discount_percentage = DecimalField('Discount Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    valid_from = DateField('Valid From', validators=[DataRequired()])
    valid_until = DateField('Valid Until', validators=[DataRequired()])
    submit = SubmitField('Create Promotion')


class SubscriptionPlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    duration = IntegerField('Duration (Months)', validators=[DataRequired(), NumberRange(min=1)])
    features = TextAreaField('Features', validators=[Optional()])
    submit = SubmitField('Create Plan')