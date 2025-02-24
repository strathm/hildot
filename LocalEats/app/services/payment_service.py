from app.models import Payment, PaymentStatus
from datetime import datetime

def initiate_payment(order_id, user_id, amount, payment_method):
    payment = Payment(
        order_id=order_id,
        user_id=user_id,
        amount=amount,
        payment_method=payment_method,
        status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    payment.save()
    return payment, None

def get_payment_by_id(payment_id):
    return Payment.query.get(payment_id)

def get_payments_by_user(user_id):
    return Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()

def update_payment_status(payment_id, status, transaction_reference=None):
    payment = Payment.query.get(payment_id)
    if not payment:
        return None, 'Payment not found'

    payment.status = status
    payment.transaction_reference = transaction_reference
    payment.updated_at = datetime.utcnow()
    payment.save()
    return payment, None

def delete_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return None, 'Payment not found'

    payment.delete()
    return True, None
