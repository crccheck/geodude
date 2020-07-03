from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from utils.address import address_components
from utils.cache import get_path, Cache


def test_get_path_can_form_path():
    address = address_components("address", "city", "state", "zip")
    assert get_path(address, "test") == "state/zip/address-test.json"


class CacheTest(TestCase):
    address = address_components("address", "city", "state", "zip")

    @classmethod
    def setUpClass(cls):
        cls.tempdir = mkdtemp(prefix="geo")

    @classmethod
    def tearDownClass(cls):
        assert cls.tempdir
        # Is this too dangerous to do? Should I rely on the OS to clean up instead?
        rmtree(cls.tempdir)

    def test_init_accepts_nonexistent_dir(self):
        Cache("test", data_dir="/tmp/non-existent-dir")
        # I could assert that the logger was called but I don't care.

    def test_get_returns_nothing_for_cold_cache(self):
        cache = Cache("test", data_dir=self.tempdir)
        assert not cache.get(self.address)

    def test_save_saves_data(self):
        cache = Cache("test", data_dir=self.tempdir)
        cache.save(self.address, {"foo": "bar"})

        assert cache.get(self.address)["foo"] == "bar"

    def test_save_can_overwrite_data(self):
        cache = Cache("test", data_dir=self.tempdir)
        cache.save(self.address, {"foo": "bar"})
        cache.save(self.address, {"foo": "baz"})

        assert cache.get(self.address)["foo"] == "baz"
