from app.models import Location
from app.utils.validators import is_valid_location

def add_location(user_id, county, estate, block, house_number, latitude=None, longitude=None):
    if not is_valid_location(county) or not is_valid_location(estate):
        return None, 'Invalid location details'

    location = Location(
        user_id=user_id,
        county=county,
        estate=estate,
        block=block,
        house_number=house_number,
        latitude=latitude,
        longitude=longitude
    )
    location.save()
    return location, None

def get_location_by_user(user_id):
    return Location.query.filter_by(user_id=user_id).first()

def update_location(location_id, county=None, estate=None, block=None, house_number=None, latitude=None, longitude=None):
    location = Location.query.get(location_id)
    if not location:
        return None, 'Location not found'

    if county and is_valid_location(county):
        location.county = county
    if estate and is_valid_location(estate):
        location.estate = estate
    if block:
        location.block = block
    if house_number:
        location.house_number = house_number
    if latitude is not None:
        location.latitude = latitude
    if longitude is not None:
        location.longitude = longitude

    location.save()
    return location, None

def delete_location(location_id):
    location = Location.query.get(location_id)
    if not location:
        return None, 'Location not found'

    location.delete()
    return True, None
