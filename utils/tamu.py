import os

import requests


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


class GeocodeException(Exception):
    pass


def geocode_address(address, force=False):
    """
    Geocode an address dict.

    Address dict should have as many of these keys:
      streetAddress, city, state, zip

    Examples:
    https://geoservices.tamu.edu/Services/Geocode/WebService/v04_01/Simple/Rest/
    """
    if not address['city'] and not address['zip']:
        raise GeocodeException("Can't look up without a city or zip")
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
    }
    params.update(address)
    headers = {
        'user-agent': 'my-little-pointies/v0.0'
    }
    response = requests.get(url, params=params, headers=headers)
    if not response.ok:
        raise GeocodeException(
            'Got a non-200 response: {}'
            .format(response.status_code))
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
