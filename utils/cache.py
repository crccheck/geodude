# TODO This module shouldn't really be using a singleton pattern
import os


def get_path(address_components, service):
    return os.path.join(
        address_components.state,
        address_components.zip,
        address_components.address + '-' + service + '.json',
    )


def get(address_components, service):
    pass


def save(address_components, service, data):
    pass
