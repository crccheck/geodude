import json
import logging
import os

from utils.json import DjangoJSONEncoder


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
        if self.data_dir and not os.path.isdir(self.data_dir):
            logger.warn('%s is not a directory, I will attempt to create it', self.data_dir)

    def get(self, address_components):
        if not self.data_dir:
            logger.debug('Missing DATA_DIR, not retrieving from cache')
            return

        full_path = os.path.join(self.data_dir, get_path(address_components, self.service))
        try:
            with open(full_path, 'r') as fp:
                return json.load(fp)

        except FileNotFoundError:
            return

    def save(self, address_components, data):
        if not self.data_dir:
            logger.debug('Missing DATA_DIR, not saving cache')
            return

        full_path = os.path.join(self.data_dir, get_path(address_components, self.service))
        dirname = os.path.dirname(full_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with open(full_path, 'w') as fp:
            json.dump(data, fp, cls=DjangoJSONEncoder)
