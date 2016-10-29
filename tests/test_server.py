from unittest.mock import patch

from server import make_app


async def test_tamu_lookup(test_client, loop):
    app = make_app(loop=loop)
    client = await test_client(app)

    with patch('utils.tamu.requests'):
        resp = await client.get('/tamu', params={'streetAddress': '123 fake st.'})

    assert resp.status == 200
