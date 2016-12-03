import asyncio
import datetime
import json
from decimal import Decimal

from aiohttp import web
from geojson import Feature, Point

from utils.address import prep_for_geocoding
from utils.cache import Cache
from utils.json import DjangoJSONEncoder
from utils.tamu import geocode_address


async def tamu_lookup(request):
    if {'address', 'city', 'state', 'zip'} - set(request.GET):
        return web.HTTPBadRequest()

    address_components = prep_for_geocoding(
        address1=request.GET.get('address'),
        address2='',
        city=request.GET.get('city'),
        state=request.GET.get('state'),
        zipcode=request.GET.get('zip'),
    )
    cache = Cache('tamu')
    result = cache.get(address_components)
    if not result:
        result = geocode_address(dict(
            streetAddress=address_components.address,
            city=address_components.city,
            state=address_components.state,
            zip=address_components.zip,
        ))
        cache.save(address_components, result)  # TODO do this in the background

    point = Point((
        Decimal(result['Longitude']), Decimal(result['Latitude'])
    ))
    feature = Feature(geometry=point, properties={
        'quality': result['NAACCRGISCoordinateQualityCode'],
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',  # poop
    })

    text = json.dumps(feature, cls=DjangoJSONEncoder)

    return web.Response(text=text)


def make_app(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/tamu', tamu_lookup)
    return app


if __name__ == '__main__':
    web.run_app(make_app())
