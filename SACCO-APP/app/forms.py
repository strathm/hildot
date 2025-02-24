from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class RegistrationForm(FlaskForm):
    """User Registration Form"""
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    national_id = StringField('National ID', validators=[DataRequired(), Length(min=6, max=20)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    occupation = StringField('Occupation', validators=[DataRequired(), Length(min=3, max=100)])
    county = StringField('County', validators=[DataRequired(), Length(min=2, max=50)])
    sub_county = StringField('Sub-County', validators=[DataRequired(), Length(min=2, max=50)])
    village_street = StringField('Village/Street', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class CreateGroupForm(FlaskForm):
    # Group details
    name = StringField('Group Name', validators=[DataRequired(), Length(min=3, max=100)])
    purpose = StringField('Purpose of the SACCO', validators=[DataRequired(), Length(min=10, max=200)])
    registration_number = StringField('Registration Number', validators=[DataRequired(), Length(min=5, max=50)])
    
    # SACCO Address
    county = StringField('County', validators=[DataRequired(), Length(min=3, max=100)])
    sub_county = StringField('Sub-County', validators=[DataRequired(), Length(min=3, max=100)])
    village = StringField('Village/Street', validators=[DataRequired(), Length(min=3, max=100)])
    
    # Admin contact info
    admin_name = StringField('Admin Name', validators=[DataRequired(), Length(min=3, max=100)])
    admin_phone_number = StringField('Admin Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    
    # SACCO start date
    start_date = DateField('Start Date', validators=[DataRequired()])
    
    # SACCO type (e.g., savings, loans, etc.)
    sacco_type = SelectField('SACCO Type', choices=[('Savings', 'Savings'), ('Loan', 'Loan'), ('Investment', 'Investment')], validators=[DataRequired()])
    
    # Submit button
    submit = SubmitField('Create Group')

class LoginForm(FlaskForm):
    """User Login Form"""
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class GroupForm(FlaskForm):
    """Form to Create a SACCO or Group"""
    name = StringField('Group Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Create Group')

class JoinGroupForm(FlaskForm):
    """Form to Request Joining a Group"""
    group_id = IntegerField('Group ID', validators=[DataRequired()])
    submit = SubmitField('Request to Join')

class SavingsForm(FlaskForm):
    """Form for Adding Savings"""
    amount = FloatField('Amount to Save (Ksh)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')

class LoanRequestForm(FlaskForm):
    """Form for Requesting a Loan"""
    amount = FloatField('Loan Amount (Ksh)', validators=[DataRequired(), NumberRange(min=500)])
    submit = SubmitField('Request Loan')

class LoanRepaymentForm(FlaskForm):
    """Form for Repaying a Loan"""
    amount = FloatField('Repayment Amount (Ksh)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Repay Loan')

class TransactionForm(FlaskForm):
    """Form for Transactions like Loan Repayments and Savings"""
    transaction_type = SelectField('Transaction Type', choices=[
        ('savings', 'Savings'),
        ('loan_repayment', 'Loan Repayment')
    ], validators=[DataRequired()])
    amount = FloatField('Amount (Ksh)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Submit')

class ApproveLoanForm(FlaskForm):
    """Admin Form to Approve Loans"""
    loan_id = IntegerField('Loan ID', validators=[DataRequired()])
    approve = SubmitField('Approve Loan')

class AssignRoleForm(FlaskForm):
    """Admin Form to Assign Roles in a Group"""
    user_id = IntegerField('User ID', validators=[DataRequired()])
    role = SelectField('Role', choices=[
        ('member', 'Member'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    submit = SubmitField('Assign Role')

class InterestDistributionForm(FlaskForm):
    """Form for Distributing Interest Earnings"""
    total_interest = FloatField('Total Interest to Distribute (Ksh)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Distribute')

class NotificationForm(FlaskForm):
    """Form for Sending Notifications"""
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Send Notification')
