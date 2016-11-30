import asyncio

from aiohttp import web

from utils.address import prep_for_geocoding
from utils.tamu import geocode_address


async def tamu_lookup(request):
    address_components = prep_for_geocoding(
        address1=request.GET.get('address'),
        address2='',
        city=request.GET.get('city'),
        state=request.GET.get('state'),
        zipcode=request.GET.get('zip'),
    )
    result = geocode_address(dict(
        streetAddress=address_components.address,
        city=address_components.city,
        state=address_components.state,
        zip=address_components.zip,
    ))
    print(result)

    return web.Response(text='hi')


def make_app(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/tamu', tamu_lookup)
    return app


if __name__ == '__main__':
    web.run_app(make_app())
