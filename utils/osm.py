import os

import requests

from . import GeocodeException


def geocode_address(address):
    params = {
        'format': 'json',
        'street': address.address,
        'city': address.city,
        'state': address.state,
        'postalcode': address.zip,
        'polygon_geojson': 1,
        'limit': 1,
    }
    headers = {
        'user-agent': 'geodude/v0.0',
    }
    response = requests.get(
        'https://nominatim.openstreetmap.org/search',
        params=params,
        headers=headers,
    )
    if not response.ok:
        raise GeocodeException('Got a non-200 response: {}'.format(response.status_code))

    return response.json()[0]
