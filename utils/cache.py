# TODO This module shouldn't really be using a singleton pattern
import logging
import os

logger = logging.getLogger(__name__)


def get_path(address_components, service):
    return os.path.join(
        address_components.state,
        address_components.zip,
        address_components.address + '-' + service + '.json',
    )


def get(address_components, service):
    data_dir = os.getenv('DATA_DIR')
    if not data_dir:
        logger.debug('Missing DATA_DIR, not retrieving from cache')
        return


def save(address_components, service, data):
    data_dir = os.getenv('DATA_DIR')
    if not data_dir:
        logger.debug('Missing DATA_DIR, not saving cache')
        return
