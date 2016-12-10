import os

import requests

from . import GeocodeException


def get_remaining_credits(api_key=os.getenv('TAMU_API_KEY')):
    """
    Get how many api credits remain for the key.

    If you run out of credits, go to:
    https://geoservices.tamu.edu/UserServices/Payments/
    """
    assert api_key
    url = (
        'https://geoservices.tamu.edu/UserServices/Payments/Balance/'
        'AccountBalanceWebServiceHttp.aspx?'
        'version=1.0&apikey={}&format=csv'.format(api_key))
    response = requests.get(url)
    assert response.ok
    key, credits = response.text.split(',')
    assert key == api_key
    return int(credits)


def geocode_address(address):
    """
    Geocode an address.

    Examples:
    https://geoservices.tamu.edu/Services/Geocode/WebService/v04_01/Simple/Rest/
    """
    api_key = os.getenv('TAMU_API_KEY')
    if not api_key:
        raise GeocodeException(
            "Can't look up without 'TAMU_API_KEY' environment variable")

    url = (
        'https://geoservices.tamu.edu/Services/Geocode/WebService/'
        'GeocoderWebServiceHttpNonParsed_V04_01.aspx'
    )
    params = {
        'apiKey': api_key,
        'version': '4.01',
        'streetAddress': address.address,
        'city': address.city,
        'state': address.state,
        'zip': address.zip,
    }
    headers = {
        'user-agent': 'geodude/v0.0',
    }
    response = requests.get(url, params=params, headers=headers)
    if not response.ok:
        raise GeocodeException('Got a non-200 response: {}'.format(response.status_code))
    fields = [
        'TransactionId',
        'Version',
        'QueryStatusCodeValue',
        'Latitude',
        'Longitude',
        'NAACCRGISCoordinateQualityCode',
        'NAACCRGISCoordinateQualityName',
        'MatchScore',
        'MatchType',
        'FeatureMatchingResultType',
        'FeatureMatchingResultCount',
        'FeatureMatchingGeographyType',
        'RegionSize',
        'RegionSizeUnits',
        'MatchedLocationType',
        'TimeTaken',
    ]
    return dict(zip(fields, response.text.split(',')))
