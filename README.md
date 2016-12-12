Geodude
=======

[![Build Status](https://travis-ci.org/crccheck/geodude.svg?branch=master)](https://travis-ci.org/crccheck/geodude)

Your geocoding buddy. Create your own personal geocoder cache!


Features
--------

- Queries against multiple services:
  - [TAMU](https://github.com/crccheck/geodude/wiki/TAMU)
  - [OSM](https://github.com/crccheck/geodude/wiki/Open-Street-Map)
- Caches results, so you don't use up your api credits
- Normalizes addresses, so you don't do unnecessary queries (US only)
- Results come back as GeoJSON


Usage
-----

Query with these get parameters:

* address
* city
* state
* zip


Examples
--------

Querying one location backend:

```
$ curl --silent 'localhost:8080/lookup/tamu?address=1100+Congress+Ave&city=austin&state=tx&zip=78701' | jq .
{
  "properties": {
    "quality": "03",
    "service": "tamu",
    "timestamp": "2016-12-10T07:39:32.374878Z",
    "cached": true
  },
  "geometry": {
    "coordinates": [
      -97.740133410666,
      30.2754538274838
    ],
    "type": "Point"
  },
  "type": "Feature"
}

```

Querying the generic endpoint:

```
$ curl --silent 'localhost:8080/lookup?address=1100+Congress+Ave&city=austin&state=tx&zip=78701' | jq .
{
  "properties": {
    "quality": "03",
    "service": "tamu",
    "timestamp": "2016-12-10T07:40:00.110244Z",
    "cached": true
  },
  "geometry": {
    "coordinates": [
      -97.740133410666,
      30.2754538274838
    ],
    "type": "Point"
  },
  "type": "Feature"
}
```

Querying the generic endpoint with no analysis, `return=collection`:

```
$ curl --silent 'localhost:8080/lookup?address=1100+Congress+Ave&city=austin&state=tx&zip=78701&return=collection' | jq .
{
  "type": "FeatureCollection",
  "features": [
    {
      "properties": {
        "quality": "03",
        "service": "tamu",
        "timestamp": "2016-12-10T07:40:20.398696Z",
        "cached": true
      },
      "geometry": {
        "coordinates": [
          -97.740133410666,
          30.2754538274838
        ],
        "type": "Point"
      },
      "type": "Feature"
    },
    {
      "properties": {
        "cached": true,
        "service": "osm",
        "timestamp": "2016-12-10T07:40:20.962264Z"
      },
      "geometry": {
        "coordinates": [
          -97.740097,
          30.275564
        ],
        "type": "Point"
      },
      "type": "Feature"
    }
  ]
}
```

Deploying this
--------------

This is meant for private use and deployed locally. Eventually, I might
document putting it behind an API gateway to lock down access. See
`example.env` for what environment variables you'll need.

### Docker

See the `docker-compose.yml` and `Dockerfile` for more examples on how to run
this.
