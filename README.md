Geodude
=======

[![Build Status](https://travis-ci.org/crccheck/geodude.svg?branch=master)](https://travis-ci.org/crccheck/geodude)

Your geocoding buddy. Create your own personal geocoder cache!


Features
--------

- Queries against multiple services (currently, only [TAMU])
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


### Example

```
$ curl 'localhost:8080/tamu?address=1100+Congress+Ave&city=austin&state=tx&zip=78701' | jq .
{
  "geometry": {
    "coordinates": [
      "-97.740133410666",
      "30.2754538274838"
    ],
    "type": "Point"
  },
  "properties": {
    "timestamp": "2016-12-03T03:42:37.605378Z",
    "quality": "03"
  },
  "type": "Feature"
}
```

### Docker

See the `docker-compose.yml` and `Dockerfile` for more examples on how to run
this.


## Deployment

This is meant for private use and deployed locally. Eventually, I might
document putting it behind an API gateway to lock down access.
