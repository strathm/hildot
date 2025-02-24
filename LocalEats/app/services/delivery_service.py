from app.models import Delivery
from datetime import datetime

def create_delivery(order_id, driver_id, estimated_delivery_time):
    delivery = Delivery(
        order_id=order_id,
        driver_id=driver_id,
        estimated_delivery_time=estimated_delivery_time,
        status='Pending',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    delivery.save()
    return delivery, None

def get_delivery_by_order(order_id):
    return Delivery.query.filter_by(order_id=order_id).first()

def get_delivery_by_driver(driver_id):
    return Delivery.query.filter_by(driver_id=driver_id).order_by(Delivery.updated_at.desc()).all()

def update_delivery_status(delivery_id, status):
    delivery = Delivery.query.get(delivery_id)
    if not delivery:
        return None, 'Delivery not found'

    delivery.status = status
    delivery.updated_at = datetime.utcnow()
    delivery.save()
    return delivery, None

def assign_driver_to_delivery(delivery_id, driver_id):
    delivery = Delivery.query.get(delivery_id)
    if not delivery:
        return None, 'Delivery not found'

    delivery.driver_id = driver_id
    delivery.updated_at = datetime.utcnow()
    delivery.save()
    return delivery, None

def delete_delivery(delivery_id):
    delivery = Delivery.query.get(delivery_id)
    if not delivery:
        return None, 'Delivery not found'

    delivery.delete()
    return True, None