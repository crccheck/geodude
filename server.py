import asyncio
import datetime
import json
import logging
import logging.config
import os
from decimal import Decimal

from aiohttp import web
from geojson import Feature, Point
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from utils.address import prep_for_geocoding
from utils.cache import Cache
from utils.json import DjangoJSONEncoder
from utils.tamu import geocode_address


logger = logging.getLogger(__name__)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': os.getenv('LOGGING_LEVEL', 'DEBUG'),
            'class': 'project_runpy.ColorizingStreamHandler',
            'formatter': 'main',
        },
    },
    'formatters': {
        'main': {
            # Docs:
            # https://docs.python.org/3/library/logging.html#logrecord-attributes
            'format': '[%(name)s] %(message)s',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'aiohttp.access': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        }
    },
})
request_count = Counter('request_total', 'Number of geocoding requests', ['service'])
request_count_cached = Counter(
    'request_cached_total',
    'Number of geocoding requests that handled from cache',
    ['service']
)


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
    is_from_cache = bool(result)
    if is_from_cache:
        request_count_cached.labels('tamu').inc()
    else:
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

    request_count.labels('tamu').inc()

    return web.Response(
        text=text,
        content_type='application/json',
        headers={
            'X-From-Cache': '1' if is_from_cache else '0',  # TODO better header name
        },
    )


async def metrics(request):
    text = generate_latest().decode('utf-8')
    return web.Response(
        text=text,
        headers={
            # We have to set this manually to avoid asyncio's charset logic
            'Counter-Type': CONTENT_TYPE_LATEST,
        }
    )


def make_app(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/tamu', tamu_lookup)
    app.router.add_get('/metrics', metrics)
    return app


if __name__ == '__main__':
    logging.info('Using data directory: %s', os.getenv('DATA_DIR'))
    web.run_app(make_app())
