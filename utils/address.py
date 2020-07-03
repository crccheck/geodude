import logging
import re
from collections import namedtuple

import usaddress


logger = logging.getLogger(__name__)
address_components = namedtuple("Address", ["address", "city", "state", "zip"])


# A zip+4 or zip+4 with a missing dash
zip_4 = re.compile(r"^\d{5}\-?(\d{4})?$")


def clean_zipcode(input):
    if zip_4.match(input):
        # malformed zip+4
        logger.debug("cleaned zip code: {}".format(input))
        return input[0:5]
    return input


def component_format(label, value):
    """
    Standardize address parts.

    Attempts to follow USPS conventions.
    """
    formatters = {
        "StreetNamePostType": lambda x: {
            "AVENUE": "AVE",
            "BOULEVARD": "BLVD",
            "DRIVE": "DR",
            "FREEWAY": "FWY",
            "FRWY": "FWY",
            "LANE": "LN",
            "PARKWAY": "PKWY",
            "PLACE": "PL",
            "ROAD": "RD",
            "STREET": "ST",
        }.get(x, x),
        "OccupancyType": lambda x: {
            "FLOOR": "FL",
            "ST": "STE",
            "SUITE": "STE",
            "SUTIE": "STE",
        }.get(x, x),
        "StreetNamePreDirectional": lambda x: {
            "EAST": "E",
            "NORTH": "N",
            "NORTHEAST": "NE",
            "NORTHWEST": "NW",
            "SOUTH": "S",
            "SOUTHEAST": "SE",
            "SOUTHWEST": "SW",
            "WEST": "W",
        }.get(x, x),
        # XXX
        "USPSBoxType": lambda x: {
            "P O BOX": "PO Box",
            "P O DRAWER": "PO Drawer",
            "PO BOX": "PO Box",
            "PO Drawer": "PO Drawer",
            "POBOX": "PO Box",
            "POST OFFICE BOX": "PO Box",
        }.get(x, x),
    }
    value = value.replace(".", "")
    if label in formatters:
        return formatters[label](value.upper())
    return value


def clean_street(address1, address2="", *, zipcode=None, strip_occupancy=False):
    """
    Clean street address.

    If a zipcode is passed in, we double check to make sure the address was
    parsed correctly.

    If strip_occupancy is true, remove components that don't affect geocoding,
    like floor, apartment, unit, etc.

    NOTE: `usaddress` was trained with full addresses, not just street address.
    """
    # matchers that rely on knowing address lines
    # Strip "care of" lines
    if re.match(r"c/o ", address1, re.IGNORECASE):
        return address2

    # concatenate line 1 and line 2
    address = "{} {}".format(address1, address2).strip()

    if not address:
        # XXX Should this be an exception?
        return address

    try:
        # Add arbitrary city/state/zip to get `usaddress` to parse the address
        # as just the street address and not a full address
        address_to_parse = (
            "{}, Austin, TX {}".format(address, zipcode) if zipcode else address
        )
        addr, type_ = usaddress.tag(address_to_parse)
    except usaddress.RepeatedLabelError:
        logger.warning("Unparseable address: {}".format(address_to_parse))
        return address

    if zipcode:
        try:
            addr.pop("PlaceName", None)
            addr.pop("StateName", None)
            guessed_zip = addr.pop("ZipCode")
            assert guessed_zip == zipcode
        except KeyError:
            logger.warning("Expected zipcode %s but found none", zipcode)
        except AssertionError:
            logger.warning(
                "Guessed the wrong zipcode {} != {}".format(guessed_zip, zipcode)
            )
    if strip_occupancy:
        addr.pop("OccupancyType", None)
        addr.pop("OccupancyIdentifier", None)
    if type_ == "Street Address":
        return " ".join(
            [component_format(label, value) for label, value in addr.items()]
        )
    elif type_ == "PO Box":
        return " ".join(
            [component_format(label, value) for label, value in addr.items()]
        )
    logger.warning("Ambiguous address: {}".format(address), extra=addr)
    return address


def prep_for_geocoding(address1, address2, city, state, zipcode):
    """
    Format an address for geocoding.

    Also serves as the lookup key in the cache.
    """
    street = clean_street(address1, address2, zipcode=zipcode, strip_occupancy=True)
    return address_components(street.upper(), city.upper(), state.upper(), zipcode)
