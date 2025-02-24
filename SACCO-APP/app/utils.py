import random
import string
from datetime import datetime, timedelta
from flask import flash
from .models import db, Savings, Loan, InterestDistribution, Notifications, User, GroupMembers, Transaction, TransactionType

# -------------------- M-PESA INTEGRATION -------------------- #

def generate_mpesa_request(amount, phone_number, transaction_type):
    """Simulates sending an M-Pesa request for payments (savings, loan repayment, etc.)"""
    mpesa_response = {
        "status": "Success",
        "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
        "amount": amount,
        "phone_number": phone_number,
        "transaction_type": transaction_type
    }
    return mpesa_response  # In production, integrate Safaricom M-Pesa API

# -------------------- INTEREST CALCULATION -------------------- #
def calculate_interest(principal, rate, time):
    return (principal * rate * time) / 100  # Simple interest formula

def calculate_interest_on_loans():
    """Calculates accrued interest on all outstanding loans and updates loan balances."""
    loans = Loan.query.filter(Loan.repayment_status == "Pending").all()
    interest_data = []

    for loan in loans:
        days_elapsed = (datetime.utcnow() - loan.requested_on).days
        daily_interest_rate = loan.interest_rate / 100 / 30  # Monthly interest divided over 30 days
        accrued_interest = loan.amount * daily_interest_rate * days_elapsed

        loan.amount += accrued_interest  # Update loan amount with accrued interest
        db.session.commit()

        interest_data.append({"loan_id": loan.id, "user_id": loan.user_id, "accrued_interest": accrued_interest})
    
    return interest_data

# -------------------- INTEREST DISTRIBUTION -------------------- #

def distribute_interest_earnings(group_id):
    """Distributes loan interest earnings among SACCO members based on their savings contribution."""
    group_savings = Savings.query.filter_by(group_id=group_id).all()
    total_savings = sum(s.amount for s in group_savings)
    total_interest_earned = sum(l.amount * (l.interest_rate / 100) for l in Loan.query.filter_by(group_id=group_id, repayment_status="Paid").all())

    if total_savings == 0 or total_interest_earned == 0:
        return {"status": "No earnings to distribute"}

    for saving in group_savings:
        user_share = (saving.amount / total_savings) * total_interest_earned
        interest_distribution = InterestDistribution(user_id=saving.user_id, group_id=group_id, total_earnings=user_share)
        db.session.add(interest_distribution)

        notify_user(saving.user_id, f"You have earned Ksh {round(user_share, 2)} from SACCO interest distribution.")

    db.session.commit()
    return {"status": "Interest distributed successfully"}

# -------------------- ROLE MANAGEMENT -------------------- #

def assign_role(user_id, group_id, role):
    """Assigns a user a new role in a SACCO group."""
    group_member = GroupMembers.query.filter_by(user_id=user_id, group_id=group_id).first()
    if group_member:
        group_member.role = role
        db.session.commit()
        notify_user(user_id, f"Your role in the group has been updated to {role}.")
        return True
    return False

# -------------------- TRANSACTIONS & NOTIFICATIONS -------------------- #

def record_transaction(user_id, group_id, transaction_type, amount):
    """Records transactions such as savings, loan payments, and loan disbursements."""
    transaction = Transaction(
        user_id=user_id,
        group_id=group_id,
        transaction_type=TransactionType[transaction_type.upper()],
        amount=amount,
        transaction_date=datetime.utcnow()
    )
    db.session.add(transaction)
    db.session.commit()
    notify_user(user_id, f"Transaction recorded: {transaction_type} of Ksh {amount}.")
    return transaction

def notify_user(user_id, message):
    """Sends notifications to users."""
    notification = Notifications(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()

def flash_messages(category, message):
    """Displays flash messages for UI feedback."""
    flash(message, category)

# -------------------- RANDOM UTILS -------------------- #

def generate_unique_code(length=8):
    """Generates a random unique code for transaction references."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def format_currency(amount):
    """Formats an amount into currency format (e.g., Ksh 1,000.00)."""
    return f"Ksh {amount:,.2f}"
