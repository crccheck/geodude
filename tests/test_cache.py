from unittest import TestCase

from utils.address import address_components
from utils.cache import get_path, Cache


def test_get_path_can_form_path():
    address = address_components('address', 'city', 'state', 'zip')
    assert get_path(address, 'test') == 'state/zip/address-test.json'


class CacheTest(TestCase):
    cache = Cache('test')

    def test_get_returns_nothing_for_cold_cache(self):
        address = address_components('address', 'city', 'state', 'zip')
        assert not self.cache.get(address)
