from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    MEMBER = "Member"
    ADMIN = "Admin"
    SUPER_ADMIN = "Super Admin"

class TransactionType(Enum):
    SAVINGS = "Savings"
    LOAN_REQUEST = "Loan Request"
    LOAN_REPAYMENT = "Loan Repayment"
    LOAN_DISBURSEMENT = "Loan Disbursement"
    INTEREST_DISTRIBUTION = "Interest Distribution"

class User(db.Model):
    """User Model for storing user details"""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    occupation = db.Column(db.String(100))
    county = db.Column(db.String(50))
    sub_county = db.Column(db.String(50))
    village_street = db.Column(db.String(100))
    role = db.Column(db.Enum(UserRole), default=UserRole.MEMBER)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

    groups = db.relationship('Group', secondary='group_members', backref='members')
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.full_name}, Role: {self.role}>"

class Group(db.Model):
    """SACCO/Group Model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    savings = db.relationship('Savings', backref='group', lazy=True)
    loans = db.relationship('Loan', backref='group', lazy=True)
    transactions = db.relationship('Transaction', backref='group', lazy=True)

    def __repr__(self):
        return f"<Group {self.name}>"

class GroupMembers(db.Model):
    """Association Table for Group Members"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.MEMBER)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)

class Savings(db.Model):
    """Savings Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    deposited_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Savings {self.amount} by User {self.user_id}>"

class Loan(db.Model):
    """Loan Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False, default=5.0)  # 5% interest
    repayment_status = db.Column(db.String(50), default="Pending")
    requested_on = db.Column(db.DateTime, default=datetime.utcnow)
    approved_on = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Loan {self.amount} for User {self.user_id}>"

class Transaction(db.Model):
    """Transaction Model for handling savings, loans, repayments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    mpesa_transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.transaction_type} - {self.amount}>"

class InterestDistribution(db.Model):
    """Model to track how loan interest earnings are distributed to members"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    total_earnings = db.Column(db.Float, nullable=False)
    distributed_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InterestDistribution {self.total_earnings} to User {self.user_id}>"

class Notifications(db.Model):
    """Notifications Model for user alerts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification for User {self.user_id}>"

class AuditLog(db.Model):
    """Model for tracking admin activities"""
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} by Admin {self.admin_id}>"
