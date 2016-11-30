from unittest.mock import patch

from server import make_app


async def test_tamu_lookup(test_client, loop):
    app = make_app(loop=loop)
    client = await test_client(app)

    with patch('utils.tamu.requests.get') as mock_get:
        resp = await client.get('/tamu', params={
            'address': '1100 Congress Ave',
            'city': 'austin',
            'state': 'tx',
            'zip': '78701',
        })
        print(mock_get.call_args)

    assert resp.status == 200
