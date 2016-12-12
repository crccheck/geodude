import os

import requests

from . import GeocodeException, USER_AGENT


def geocode_address(address):
    """
    Geocode an address.

    http://wiki.openstreetmap.org/wiki/Nominatim
    """
    params = {
        'format': 'json',
        'street': address.address,
        'city': address.city,
        'state': address.state,
        'postalcode': address.zip,
        'polygon_geojson': 1,  # TODO this doesn't appear to do anything
        'limit': 1,
    }
    if os.getenv('EMAIL'):
        params['email'] = os.getenv('EMAIL')
    headers = {
        'user-agent': USER_AGENT,
    }
    response = requests.get(
        'https://nominatim.openstreetmap.org/search',
        params=params,
        headers=headers,
    )
    if not response.ok:
        raise GeocodeException('Got a non-200 response: {}'.format(response.status_code))

    return response.json()[0]
