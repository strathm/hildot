from app.models import Restaurant, MenuItem, Order
from datetime import datetime
from app.utils.validators import is_valid_name, is_valid_location

def register_restaurant(owner_id, name, location, delivery_radius):
    if not is_valid_name(name):
        return None, 'Invalid restaurant name'
    if not is_valid_location(location):
        return None, 'Invalid location'

    restaurant = Restaurant(owner_id=owner_id, name=name, location=location, delivery_radius=delivery_radius)
    restaurant.save()
    return restaurant, None

def create_restaurant_service(form, user):
    return register_restaurant(user.id, form.name.data, form.location.data, form.delivery_radius.data)

def get_restaurant_service(restaurant_id):
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        return None, 'Restaurant not found'
    return restaurant, None

def get_restaurant_by_id(restaurant_id):
    return Restaurant.query.get(restaurant_id)

def get_restaurants_by_owner(owner):
    return Restaurant.query.filter_by(owner=owner).all()

def add_menu_item_service(form, restaurant):
    return add_menu_item(restaurant.id, form.name.data, form.description.data, form.price.data, form.image_url.data)

def add_menu_item(restaurant_id, name, description, price, image_url):
    if not is_valid_name(name):
        return None, 'Invalid item name'

    menu_item = MenuItem(restaurant_id=restaurant_id, name=name, description=description, price=price, image_url=image_url)
    menu_item.save()
    return menu_item, None

def get_menu_items_by_restaurant(restaurant_id):
    return MenuItem.query.filter_by(restaurant_id=restaurant_id).all()

def get_menu_item_by_id(menu_item_id):
    return MenuItem.query.get(menu_item_id)

def update_menu_item(menu_item_id, name=None, description=None, price=None, image_url=None):
    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        return None, 'Menu item not found'

    if name and is_valid_name(name):
        menu_item.name = name
    if description:
        menu_item.description = description
    if price is not None:
        menu_item.price = price
    if image_url:
        menu_item.image_url = image_url

    menu_item.save()
    return menu_item, None

def delete_menu_item(menu_item_id):
    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        return None, 'Menu item not found'

    menu_item.delete()
    return True, None

def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return None, 'Restaurant not found'

    restaurant.delete()
    return True, None

def update_order_status_service(order_id, status):
    order = Order.query.get(order_id)
    if not order:
        return None, 'Order not found'

    order.status = status
    order.updated_at = datetime.utcnow()
    order.save()
    return order, None

def track_order_service(order_id):
    order = Order.query.get(order_id)
    if not order:
        return None, 'Order not found'

    return {'status': order.status, 'updated_at': order.updated_at}, None
