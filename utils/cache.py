import logging
import os

logger = logging.getLogger(__name__)


def get_path(address_components, service):
    return os.path.join(
        address_components.state,
        address_components.zip,
        address_components.address + '-' + service + '.json',
    )


class Cache:
    def __init__(self, service, *, data_dir=None):
        self.service = service
        self.data_dir = data_dir or os.getenv('DATA_DIR')

    def get(self, address_components):
        if not self.data_dir:
            logger.debug('Missing DATA_DIR, not retrieving from cache')
            return

    def save(self, address_components, data):
        if not self.data_dir:
            logger.debug('Missing DATA_DIR, not saving cache')
            return
