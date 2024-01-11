import configparser
from pathlib import Path


def read_config(section: str) -> dict:
    config = configparser.ConfigParser()
    if Path('config.ini').exists():
        config.read('config.ini')
        return dict(par for par in config.items(section))
    else:
        raise RuntimeError(
            'config.ini not find, copy defaultconfig.ini and write in parametrs')
