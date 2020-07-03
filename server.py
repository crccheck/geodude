import asyncio
import datetime
import json
import logging
import logging.config
import os
from decimal import Decimal

from aiohttp import web
from aiohttp_swagger import setup_swagger, swagger_path
from geojson import Feature, FeatureCollection, Point
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from utils.address import prep_for_geocoding
from utils.cache import Cache
from utils.json import GeoJSONEncoder
from utils.osm import geocode_address as osm_geocode_address
from utils.tamu import geocode_address as tamu_geocode_address


logger = logging.getLogger(__name__)
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "level": os.getenv("LOGGING_LEVEL", "DEBUG"),
                "class": "project_runpy.ColorizingStreamHandler",
                "formatter": "main",
            },
        },
        "formatters": {
            "main": {
                # Docs:
                # https://docs.python.org/3/library/logging.html#logrecord-attributes
                "format": "[%(name)s] %(message)s",
            },
        },
        "loggers": {
            "": {"level": "INFO", "handlers": ["console"],},
            "aiohttp.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
)
request_count = Counter("request_total", "Number of geocoding requests", ["service"])
request_count_cached = Counter(
    "request_cached_total",
    "Number of geocoding requests that handled from cache",
    ["service"],
)


class Lookup(web.View):
    name = ""

    def get_address(self):
        if {"address", "city", "state", "zip"} - set(self.request.query):
            return  # TODO raise exception

        return prep_for_geocoding(
            address1=self.request.query.get("address"),
            address2="",
            city=self.request.query.get("city"),
            state=self.request.query.get("state"),
            zipcode=self.request.query.get("zip"),
        )

    async def get(self):
        address_components = self.get_address()
        if not address_components:
            return web.HTTPBadRequest()

        feature = await self.get_from_backend(address_components)

        return web.Response(
            text=json.dumps(feature, cls=GeoJSONEncoder),
            content_type="application/json",
            headers={
                # TODO better header name
                "X-From-Cache": "1"
                if feature["properties"]["cached"]
                else "0",
            },
        )


@swagger_path("swagger/TAMULookup.yml")
class TAMULookup(Lookup):
    name = "tamu"

    @staticmethod
    async def get_from_backend(address_components):
        cache = Cache(TAMULookup.name)
        result = cache.get(address_components)
        is_cached = bool(result)
        if is_cached:
            request_count_cached.labels(TAMULookup.name).inc()
        else:
            result = tamu_geocode_address(address_components)
            cache.save(address_components, result)  # TODO do this in the background
        request_count.labels(TAMULookup.name).inc()

        point = Point((Decimal(result["Longitude"]), Decimal(result["Latitude"])))
        feature = Feature(
            geometry=point,
            properties={
                "service": TAMULookup.name,
                "quality": result["NAACCRGISCoordinateQualityCode"],
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",  # poop
                "cached": is_cached,  # should this be a timestamp?
            },
        )

        return feature


@swagger_path("swagger/OSMLookup.yml")
class OSMLookup(Lookup):
    name = "osm"

    @staticmethod
    async def get_from_backend(address_components):
        cache = Cache(OSMLookup.name)
        result = cache.get(address_components)
        is_cached = bool(result)
        if is_cached:
            request_count_cached.labels(OSMLookup.name).inc()
        else:
            result = osm_geocode_address(address_components)
            cache.save(address_components, result)  # TODO do this in the background
        request_count.labels(OSMLookup.name).inc()

        point = Point((Decimal(result["lon"]), Decimal(result["lat"])))
        feature = Feature(
            geometry=point,
            properties={
                "service": OSMLookup.name,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",  # poop
                "cached": is_cached,  # should this be a timestamp?
            },
        )

        return feature


@swagger_path("swagger/MasterLookup.yml")
class MasterLookup(Lookup):
    async def get(self):
        address_components = self.get_address()

        loop = self.request.app.loop  # alias
        backends = [TAMULookup, OSMLookup]
        all_features = await asyncio.gather(
            *map(
                lambda x: asyncio.ensure_future(
                    x.get_from_backend(address_components), loop=loop
                ),
                backends,
            )
        )

        if self.request.query.get("return") == "collection":
            data = FeatureCollection(all_features)
        else:
            # TODO average features
            data = all_features[0]

        return web.Response(
            text=json.dumps(data, cls=GeoJSONEncoder), content_type="application/json",
        )


async def metrics(request):
    text = generate_latest().decode("utf-8")
    return web.Response(
        text=text,
        headers={
            # We have to set this manually to avoid asyncio's charset logic
            "Counter-Type": CONTENT_TYPE_LATEST,
        },
    )


def make_app(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get("/lookup", MasterLookup)
    app.router.add_get("/lookup/osm", OSMLookup)
    app.router.add_get("/lookup/tamu", TAMULookup)
    app.router.add_get("/metrics", metrics)
    setup_swagger(
        app, swagger_url="/doc", title="hiya",
    )
    return app


if __name__ == "__main__":
    logging.info("Using data directory: %s", os.getenv("DATA_DIR"))
    web.run_app(make_app())
