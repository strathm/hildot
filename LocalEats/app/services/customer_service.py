from app.models import Customer
from app.utils.validators import is_valid_name, is_valid_location, is_valid_phone

def register_customer(user_id, name, phone, location):
    if not is_valid_name(name):
        return None, 'Invalid name'
    if not is_valid_phone(phone):
        return None, 'Invalid phone number'
    if not is_valid_location(location):
        return None, 'Invalid location'

    customer = Customer(user_id=user_id, name=name, phone=phone, location=location)
    customer.save()
    return customer, None

def get_customer_by_id(customer_id):
    return Customer.query.get(customer_id)

def update_customer(customer_id, name=None, phone=None, location=None):
    customer = Customer.query.get(customer_id)
    if not customer:
        return None, 'Customer not found'

    if name and is_valid_name(name):
        customer.name = name
    if phone and is_valid_phone(phone):
        customer.phone = phone
    if location and is_valid_location(location):
        customer.location = location

    customer.save()
    return customer, None
