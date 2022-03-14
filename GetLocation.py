# pylint: disable=invalid-name
"""
Geocoder using GeoPy package
"""
from geopy.geocoders import Nominatim  # pylint: disable=import-error
from geopy.extra.rate_limiter import RateLimiter  # pylint: disable=import-error


def get_location(name):
    """
    get exact location of a settlement
    :param name:
    :return:
    """
    geocoder = RateLimiter(Nominatim(user_agent="sth").geocode, min_delay_seconds=1)
    location = geocoder(name)
    if location is None or location.longitude < 20:
        location = geocoder('Львів')
    return location.latitude, location.longitude
