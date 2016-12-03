from utils.address import address_components
from utils import cache


def test_get_path_can_form_path():
    address = address_components('address', 'city', 'state', 'zip')
    assert cache.get_path(address, 'test') == 'state/zip/address-test.json'


def test_get_returns_nothing_for_cold_cache():
    address = address_components('address', 'city', 'state', 'zip')
    assert not cache.get(address, 'test')
