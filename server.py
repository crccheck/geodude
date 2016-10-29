import asyncio

from aiohttp import web

from utils import tamu


async def tamu_lookup(request):
    print(request.GET)
    # import ipdb; ipdb.sset_trace()
    return web.Response(text='hi')


def make_app(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/tamu', tamu_lookup)
    return app


if __name__ == '__main__':
    web.run_app(make_app())
