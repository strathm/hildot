from app.models import OrderTracking
from datetime import datetime

def create_tracking_entry(order_id, status, location=None):
    tracking_entry = OrderTracking(
        order_id=order_id,
        status=status,
        location=location,
        timestamp=datetime.utcnow()
    )
    tracking_entry.save()
    return tracking_entry, None

def get_tracking_entries_by_order(order_id):
    return OrderTracking.query.filter_by(order_id=order_id).order_by(OrderTracking.timestamp.asc()).all()

def get_latest_tracking_entry(order_id):
    return OrderTracking.query.filter_by(order_id=order_id).order_by(OrderTracking.timestamp.desc()).first()

def update_tracking_entry(entry_id, status=None, location=None):
    tracking_entry = OrderTracking.query.get(entry_id)
    if not tracking_entry:
        return None, 'Tracking entry not found'

    if status:
        tracking_entry.status = status
    if location:
        tracking_entry.location = location
    tracking_entry.timestamp = datetime.utcnow()
    tracking_entry.save()
    return tracking_entry, None

def delete_tracking_entry(entry_id):
    tracking_entry = OrderTracking.query.get(entry_id)
    if not tracking_entry:
        return None, 'Tracking entry not found'

    tracking_entry.delete()
    return True, None
