from aiohttp import web


async def handle(request):
    return web.Response(text='hi')


app = web.Application()
app.router.add_get('/', handle)

web.run_app(app)
