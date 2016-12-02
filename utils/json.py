"""
Django's JSON Encoder

https://github.com/django/django/blob/master/django/core/serializers/json.py
"""
import datetime
import decimal
import json


class DjangoJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            # if is_aware(o):
            #     raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        # elif isinstance(o, datetime.timedelta):
        #     return duration_iso_string(o)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        # elif isinstance(o, uuid.UUID):
        #     return str(o)
        # elif isinstance(o, Promise):
        #     return six.text_type(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)
