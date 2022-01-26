'''get ccxt config'''
# pylint: disable=[invalid-name, too-many-instance-attributes]
import logging
from dataclasses import dataclass

from tracker.core.utils import load_yml

logger = logging.getLogger(__name__)

CONFIG_LOCATION = './config/ccxt_config.yml'


@dataclass
class CCXTConfig:
    '''defines the config file attributes'''
    limits: dict[str, int]  # exchange_name: read_limit
    update_interval: float
    pagination: dict[str, str]  # exchange_name: pagination_method

    @classmethod
    def create(cls, config_file_location=CONFIG_LOCATION) -> 'CCXTConfig':
        '''provides a default method to create ccxt config class'''
        config = load_yml(config_file_location)
        return cls(**config)


def test() -> None:
    '''module test'''
    config = CCXTConfig.create()
    print(config)


if __name__ == '__main__':
    test()
