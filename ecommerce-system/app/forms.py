from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField, 
    FloatField, IntegerField, SelectField, FileField, BooleanField, HiddenField, DecimalField, EmailField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Optional
)
from flask_wtf.file import FileAllowed
from .models import Category, User


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
class FeedbackForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    comment = TextAreaField('Comment', validators=[DataRequired()])
    rating = SelectField(
        'Rating', 
        choices=[('', 'Select Rating'), ('5', '5 - Excellent'), ('4', '4 - Very Good'), ('3', '3 - Good'), ('2', '2 - Fair'), ('1', '1 - Poor')],
        validators=[Optional()]
    )
    submit = SubmitField('Submit Feedback')
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
# User Registration Form
class RegistrationForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])  # Enforce strong password
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    county = StringField('County', validators=[DataRequired(), Length(max=100)])
    subcounty = StringField('Sub-county', validators=[DataRequired(), Length(max=100)])
    street = StringField('Street or Known Area', validators=[DataRequired(), Length(max=200)])

    submit = SubmitField('Register')
class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = DecimalField('Price', places=2, validators=[DataRequired()])
    quantity = IntegerField('Stock Quantity', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()], choices=[])  # Default empty list
    is_available = BooleanField('Available for Sale')
    image = FileField('Upload Image')
class CSRFForm(FlaskForm):
    """A simple form for CSRF token validation."""
    pass
class CheckoutForm(FlaskForm):
    pass  # No additional fields needed for CSRF protection  

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    role = SelectField(
        'Role', 
        choices=[('seller', 'Seller')], 
        default='seller', 
        validators=[DataRequired()]
    )

    submit = SubmitField('Register')

    # Custom validation to ensure unique email and username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValueError("Username already exists. Please choose another.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValueError("Email already exists. Please choose another.")
class ManageProductForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_sold = IntegerField('Quantity Sold', validators=[NumberRange(min=0)], default=0)
    quantity_added = IntegerField('Quantity Added', validators=[NumberRange(min=0)], default=0)
    submit = SubmitField('Update Product')


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    occupation = StringField("Occupation")
    submit = SubmitField("Update Profile")
# Login Form
class LoginForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Placeholder CSRF protection for Cart Form
class CartForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection

# Request Item Form
class RequestItemForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Request')

# Edit User Form
class EditUserForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    username = StringField('Username', validators=[DataRequired()])
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Save Changes')

# Update Profile Form
class UpdateProfileForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    password = PasswordField('New Password', validators=[Optional(), Length(min=8, max=128), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Update Profile')

# Contact Form
class ContactForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')

# Add Product Form
class AddProductForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Product Description', validators=[Optional(), Length(max=1000)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    image = FileField('Product Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Only images allowed!')])
    submit = SubmitField('Add Product')

    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(0, 'Select Category')] + [(category.id, category.name) for category in Category.query.all()]

# Bulk Upload Form
class BulkUploadForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    file = FileField("Upload File (PDF or Word)", validators=[DataRequired(), FileAllowed(['pdf', 'docx'], 'Only PDF or Word documents!')])
    submit = SubmitField("Upload Products")

# Edit Product Form
class EditProductForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Product Description', validators=[Optional(), Length(max=1000)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    image = FileField('Update Product Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Only images allowed!')])
    submit = SubmitField('Update Product')

# Category Forms
class AddCategoryForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Category Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Add Category')

class EditCategoryForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Category Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Category')

# Customer Request Form
class CustomerRequestForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Additional Details', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Request')

# Update Stock Form
class UpdateStockForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_change = IntegerField('Quantity Change', validators=[DataRequired()])
    submit = SubmitField('Update Stock')

# Feedback Form


# Search Form
class SearchForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    query = StringField('Search', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Search')

# Admin Login Form
class AdminLoginForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    username = StringField('Admin Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Admin Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Login as Admin')

# Order Status Update Form
class UpdateOrderStatusForm(FlaskForm):
    csrf_token = HiddenField()  # CSRF protection
    order_id = SelectField('Order', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Delivered', 'Delivered')], validators=[DataRequired()])
    submit = SubmitField('Update Status')
