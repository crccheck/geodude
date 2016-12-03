from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from utils.address import address_components
from utils.cache import get_path, Cache


def test_get_path_can_form_path():
    address = address_components('address', 'city', 'state', 'zip')
    assert get_path(address, 'test') == 'state/zip/address-test.json'


class CacheTest(TestCase):
    address = address_components('address', 'city', 'state', 'zip')

    @classmethod
    def setUpClass(cls):
        cls.tempdir = mkdtemp(prefix='geo')
        cls.cache = Cache('test', data_dir=cls.tempdir)

    @classmethod
    def tearDownClass(cls):
        assert cls.tempdir
        # Is this too dangerous to do? Should I rely on the OS to clean up instead?
        rmtree(cls.tempdir)

    def test_get_returns_nothing_for_cold_cache(self):
        assert not self.cache.get(self.address)

    def test_save_saves_data(self):
        self.cache.save(self.address, {'foo': 'bar'})

        assert self.cache.get(self.address)['foo'] == 'bar'
