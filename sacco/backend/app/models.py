from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User roles for role-based access control
class UserRole:
    ADMIN = "admin"
    MEMBER = "member"
    TREASURER = "treasurer"

# SACCO model
class Sacco(db.Model):
    __tablename__ = "saccos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Primary admin
    
    members = db.relationship("User", backref="sacco", lazy=True)
    loans = db.relationship("Loan", backref="sacco", lazy=True)
    savings = db.relationship("Savings", backref="sacco", lazy=True)
    transactions = db.relationship("Transaction", backref="sacco", lazy=True)
    meetings = db.relationship("Meeting", backref="sacco", lazy=True)  # Meetings

# User model (Admin and Members)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, db.ForeignKey("saccos.id"), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default=UserRole.MEMBER)  # Default role is member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    savings = db.relationship("Savings", backref="user", lazy=True)
    loans = db.relationship("Loan", backref="user", lazy=True)
    transactions = db.relationship("Transaction", backref="user", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)  # Notifications

# Savings model
class Savings(db.Model):
    __tablename__ = "savings"
    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, db.ForeignKey("saccos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    total_earnings = db.Column(db.Float, nullable=True)  # Earnings generated from the savings

# Loan model
class Loan(db.Model):
    __tablename__ = "loans"
    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, db.ForeignKey("saccos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)  # Loan amount
    interest_rate = db.Column(db.Float, nullable=False)  # Interest rate per month (e.g., 11%)
    duration_months = db.Column(db.Integer, nullable=False)  # Loan duration in months
    status = db.Column(db.String(20), default="pending")  # e.g., "approved", "rejected", "paid"
    issued_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    grace_period_days = db.Column(db.Integer, default=7)  # Grace period after due date before penalties apply
    total_amount_due = db.Column(db.Float, nullable=True)  # Total amount to repay (principal + interest)
    late_penalty_rate = db.Column(db.Float, default=0.05)  # Late penalty rate per month after due date

    # Calculate total amount due based on interest rate and loan duration
    @property
    def calculate_total_due(self):
        # Calculate interest over the loan duration
        total_interest = self.principal_amount * self.interest_rate * self.duration_months / 100
        return self.principal_amount + total_interest

    # Calculate if the loan is overdue
    @property
    def is_overdue(self):
        current_time = datetime.utcnow()
        if self.due_date and current_time > self.due_date:
            overdue_days = (current_time - self.due_date).days
            return overdue_days
        return 0

    # Calculate penalties based on overdue time
    @property
    def calculate_penalty(self):
        overdue_days = self.is_overdue
        if overdue_days > 0:
            months_overdue = (overdue_days // 30) + 1  # Round up to the nearest month
            penalty = self.principal_amount * self.late_penalty_rate * months_overdue
            return penalty
        return 0

    # Update the total amount due to include the penalty (if any)
    @property
    def total_amount_due_with_penalty(self):
        return self.calculate_total_due + self.calculate_penalty
    
    repayments = db.relationship("LoanRepayment", backref="loan", lazy=True)

# Loan Repayment model (to track repayments for loans)
class LoanRepayment(db.Model):
    __tablename__ = "loan_repayments"
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey("loans.id"), nullable=False)
    repayment_amount = db.Column(db.Float, nullable=False)
    repayment_date = db.Column(db.DateTime, default=datetime.utcnow)

# Transactions model
class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, db.ForeignKey("saccos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # "deposit", "withdrawal", "loan_repayment"
    mpesa_reference = db.Column(db.String(100), unique=True, nullable=True)  # Reference for M-Pesa transactions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Interest Sharing model
class InterestDistribution(db.Model):
    __tablename__ = "interest_distribution"
    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, db.ForeignKey("saccos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_interest_earned = db.Column(db.Float, nullable=False)  # Based on user savings
    distributed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Meeting model (for scheduling meetings)
class Meeting(db.Model):
    __tablename__ = "meetings"
    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, db.ForeignKey("saccos.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    meeting_date = db.Column(db.DateTime, nullable=False)  # Date and time of the meeting
    location = db.Column(db.String(200), nullable=True)  # Optional location
    description = db.Column(db.Text, nullable=True)  # Optional description of the meeting
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    attendees = db.relationship("MeetingAttendee", backref="meeting", lazy=True)  # Attendees
    
# Meeting Attendees model (for tracking attendees)
class MeetingAttendee(db.Model):
    __tablename__ = "meeting_attendees"
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    attended_at = db.Column(db.DateTime, default=datetime.utcnow)

# Notification model (to track notifications for users)
class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)  # The notification message
    is_read = db.Column(db.Boolean, default=False)  # Status of the notification (read or unread)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Activity Log model (to track system activity or changes)
class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(255), nullable=False)  # Action description (e.g., "approved loan")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Audit Trail for Transactions
class AuditTrail(db.Model):
    __tablename__ = "audit_trail"
    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, db.ForeignKey("saccos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(200), nullable=False)  # e.g., "approved loan", "updated savings"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
