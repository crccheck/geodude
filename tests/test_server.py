from unittest.mock import patch, MagicMock

from server import make_app

# Why isn't there a noqa-next-line ?
TAMU_SUCCESS= '139863c0-e12d-4ace-a0aa-7ad84ca88a4e,4.1,200,30.2754538274838,-97.740133410666,03,StreetSegmentInterpolation,100,Exact,Success,1,StreetSegment,1602.31620959309,Meters,LOCATION_TYPE_STREET_ADDRESS,0.0120012,'  # noqa


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


async def test_tamu_lookup_errors_with_bad_input(test_client, loop):
    app = make_app(loop=loop)
    client = await test_client(app)

    resp = await client.get('/lookup/tamu')

    assert resp.status == 400


async def test_tamu_lookup(test_client, loop):
    app = make_app(loop=loop)
    client = await test_client(app)
    mock_response = MagicMock(
        ok=True,
        text=TAMU_SUCCESS,
    )

    with patch('utils.tamu.requests.get') as mock_get:
        mock_get.return_value = mock_response
        resp = await client.get('/lookup/tamu', params={
            'address': '1100 Congress Ave',
            'city': 'austin',
            'state': 'tx',
            'zip': '78701',
        })

    assert resp.status == 200
    assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'


async def test_lookup_returns_service_response(test_client, loop):
    app = make_app(loop=loop)
    client = await test_client(app)

    mock_get = AsyncMock(return_value={'foo': 'bar'})

    with patch('server.TAMULookup.get_from_backend', new=mock_get):
        resp = await client.get('/lookup', params={
            'address': '1100 Congress Ave',
            'city': 'austin',
            'state': 'tx',
            'zip': '78701',
        })
    out = await resp.json()

    assert resp.status == 200
    assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'
    assert out == {'foo': 'bar'}


async def test_lookup_returns_all_service_responses(test_client, loop):
    app = make_app(loop=loop)
    client = await test_client(app)

    mock_osm = AsyncMock(return_value={'foo': 'osm'})
    mock_tamu = AsyncMock(return_value={'foo': 'tamu'})

    with patch('server.OSMLookup.get_from_backend', new=mock_osm):
        with patch('server.TAMULookup.get_from_backend', new=mock_tamu):
            resp = await client.get('/lookup', params={
                'address': '1100 Congress Ave',
                'city': 'austin',
                'state': 'tx',
                'zip': '78701',
                'return': 'collection',
            })
    out = await resp.json()

    assert resp.status == 200
    assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'
    assert out == {'features': [{'foo': 'tamu'}, {'foo': 'osm'}], 'type': 'FeatureCollection'}


async def test_metrics(test_client, loop):
    app = make_app(loop=loop)
    client = await test_client(app)

    resp = await client.get('/metrics')

    assert resp.status == 200
    assert resp.headers['Content-Type'] == 'text/plain; charset=utf-8'
