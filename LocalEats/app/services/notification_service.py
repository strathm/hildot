from app.models import Notification
from datetime import datetime

def create_notification(user_id, message, order_id=None):
    notification = Notification(
        user_id=user_id,
        message=message,
        order_id=order_id,
        is_read=False,
        created_at=datetime.utcnow()
    )
    notification.save()
    return notification, None

def get_notifications_by_user(user_id):
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

def get_unread_notifications_by_user(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).all()

def mark_notification_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return None, 'Notification not found'

    notification.is_read = True
    notification.save()
    return notification, None

def mark_all_notifications_as_read(user_id):
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    for notification in notifications:
        notification.is_read = True
        notification.save()
    return True, None

def delete_notification(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return None, 'Notification not found'

    notification.delete()
    return True, None

def delete_all_notifications_by_user(user_id):
    notifications = Notification.query.filter_by(user_id=user_id).all()
    for notification in notifications:
        notification.delete()
    return True, None